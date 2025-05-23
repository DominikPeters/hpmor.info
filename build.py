# Builds HTML files & uploads to server

from __future__ import unicode_literals, print_function
from builtins import open, bytes
from tqdm import tqdm, trange
from ftplib import FTP
import datetime
import sys
from ruamel.yaml import YAML
import os

yaml = YAML()

chapter = {}
notes = {}

vscode_prefix = "https://github.dev/DominikPeters/hpmor.info/blob/master/yaml"
PRINT_VSCODE_LINKS = True
vscode_link = {}

print("Read YAML..")
comment_ids = set()
for i in trange(1, 123):
    with open(f"yaml/{i}.yaml", "r") as f:
        chapter[i] = yaml.load(f)
        chapter[i]["num_notes"] = 0
    # make vscode deeplinks for paragraphs
    with open(f"yaml/{i}.yaml", "r") as f:
        for lineno, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            if line[0] != " " and line[-1] == ":":
                number = line[:-1]
                if number.isdigit():
                    # vscode_link[int(number)] = f"{vscode_prefix}/{i}.yaml#L{lineno+1}"
                    # if int(number) - 1 in vscode_link:
                    #     vscode_link[int(number) - 1] += f"-L{lineno}"
                    vscode_link[int(number)] = f"https://github.com/DominikPeters/hpmor.info/issues/new?assignees=&labels=note-proposal&projects=&template=note-proposal.yml&paragraph_number={number}&title=Chapter+{i}"

def note2string(note):
    if note["type"] == "reddit":
        html = '<div class="note">'
        points = f'{note["score"]} point ' if note["score"] == 1 else f'{note["score"]} points ' if "score" in note else ""
        html += f"""<span class="meta">
            <a href="{note["url"]}"><b>{note["author"]}</b> {points}{note["date"].replace("/", "-")}</a>
        </span>"""
        html += note["text"]
        if "replies" in note:
            for child in note["replies"]:
                html += note2string(child)
        html += "</div>"
    elif note["type"] == "original":
        html = f'<div class="note">{note["text"]}</div>'
    elif note["type"] == "note_needed":
        html = f"""<div class="note note-needed">
            <div class="note-needed-header">
                [note needed]
                <span class="note-needed-date">{note["date"].replace("/", "-")}</span> 
                <span class="note-needed-add"><a href="{vscode_link[note["para"]]}">add note</a></span>
            </div>
            <div class="note-needed-explanation">{note["text"]}</div>
        </div>"""
    else:
        raise Exception(f"Unknown note type: {note['type']}")
    return html

# generate html
print("Generate HTML..")
header = open("template/header.html","r").read()
footer = open("template/footer.html","r").read()
# full book html
full = header.replace("[NR]", "1&ndash;122") \
             .replace("[TITLE]", "Harry Potter and the Methods of Rationality")
full = full.replace("[CHAPTERLINKS]", "<div class='chapter-context-nav'><span class='go-home'><a href='/'>Home</a></span></div>") \
           .replace("[HEAD]", "") \
           .replace("[FIRST_NOTE_LINK]", "")
htmls = {}
for i in trange(1, 123):
    html = header.replace("[NR]", str(i)).replace("[TITLE]", chapter[i]["title"])
    head = ""
    chapterlinks = "<div class='chapter-context-nav'>"
    if i != 1:
        chapterlinks += f'<span class="prev-chapter"><a href="/chapter/{i-1}">&larr; {i-1}</a></span>'
        head += f'<link rel="prerender" href="/chapter/{i-1}">'
    chapterlinks += '<span class="go-home"><a href="/">Home</a></span>'
    if i != 122:
        chapterlinks += f'<span class="next-chapter"><a href="/chapter/{i+1}">{i+1} &rarr;</a></span>'
        head += f'<link rel="prerender" href="/chapter/{i+1}">'
    chapterlinks += "</div>"
    html = html.replace("[CHAPTERLINKS]", chapterlinks)
    html = html.replace("[HEAD]", head)
    chapter[i]["num_notes"] = 0
    chapter_paras = range(int(chapter[i]["first_para"]),int(chapter[i]["last_para"]+1))
    active_paras = set()
    for para in chapter_paras:
        if "notes" in chapter[i][para]:
            active_paras.add(para)
    active_paras = sorted(active_paras)
    if active_paras:
        html = html.replace("[FIRST_NOTE_LINK]", f'<div id="jump-to-first-note"><a href="#{active_paras[0]}">first note &darr;</a></div>')
    else:
        html = html.replace("[FIRST_NOTE_LINK]", "")
    boilerplate = html
    html = ""
    full += f"<h2>{chapter[i]['title']}</h2>"
    interesting_paras = set(para for para in chapter_paras if any(para+offset in active_paras for offset in [-3,-2,-1,0,1,2]) \
                                or (para-4 in active_paras and sum(len(chapter[i][para+offset]["text"]) for offset in [-4,-3,-2,-1]) < 200))
    for para in chapter_paras:
        if para in interesting_paras and (para-1) not in interesting_paras and para not in active_paras:
            html += f'<div class="expand-button"><a href="#{para}" onclick="expand()">+</a></div>'
            html += '<div class="paragraph fade-in">'
        elif para in interesting_paras and (para+1) not in interesting_paras and para not in active_paras:
            html += '<div class="paragraph fade-out">'
        elif para in interesting_paras:
            html += '<div class="paragraph">'
        else:
            html += '<div class="paragraph collapsible">'
        if "notes" in chapter[i][para]:
            html += '<div class="notes">'
            if para != active_paras[0]:
                prev = active_paras[active_paras.index(para) - 1]
                if prev < para - 2 and prev - 2 > chapter[i]["first_para"]:
                    html += f'<div class="jump-to-prev-note"><a href="#{prev-2}">&uarr;</a></div>'
            for note in chapter[i][para]["notes"]:
                chapter[i]["num_notes"] += 1
                note["para"] = para
                html += note2string(note)
            if para != active_paras[-1]:
                following = active_paras[active_paras.index(para) + 1]
                if following > para + 2 and following - 2 < chapter[i]["last_para"]:
                    html += f'<div class="jump-to-next-note"><a href="#{following-2}">&darr;</a></div>'
            html += "</div>"
        else:
            pass
            # html += '<div class="notes no-notes"><a>annotate on reddit</a></div>'
        html += f'\n<p>\n<a id="{para}"></a>'
        # old version with links to reddit
        # html += '<span class="para-number"><a href="javascript:showCommentField(' + str(para) + ')" class="para-anchor">+</a> <a href="https://www.reddit.com/r/hpmor_annotated/comments/' + str(chapter[i]["reddit_posts"][-1]) + '/" class="para-anchor">&#9741;</a> '+str(para)+' '
        html += f'<span class="para-number">{para} '
        html += f'<a href="#{para}" class="para-anchor">&para;</a> \n'
        if PRINT_VSCODE_LINKS:
            html += f'<a href="{vscode_link[para]}" class="para-anchor">+</a> \n'
        html += '</span>\n'
        html += chapter[i][para]["text"]
        # html += ' <a href="javascript:showCommentField(' + str(para) + ')" class="comment-shower">+</a>'
        html += "\n</p>"
        # add comment field
        # html += "<div class='comment-field' id='comment-"+str(para)+"'><textarea id='textarea-"+str(para)+"' rows='4' cols='60'>"+str(para)+"</textarea><button id='submit-"+str(para)+"' onclick='javascript:submitComment("+str(para)+")'>Submit</button><div id='response-"+str(para)+"'></div></div>"
        html += "\n</div>"
        if interesting_paras and para == max(interesting_paras):
            html += f'<div class="expand-button" id="last-expand-button"><a href="#{para}" onclick="expand()">+</a></div>'
        if "draw-line-after-paragraph" in chapter[i][para]:
            if para in interesting_paras:
                html += '<div>'
            else:
                html += '<div class="collapsible">'
            html += '<hr>'
            html += '</div>'
    full += html
    html = boilerplate + html
    html += footer.replace("[CHAPTERLINKS]", chapterlinks).replace("[NR]", str(i))
    htmls[i] = html

full += footer.replace("[CHAPTERLINKS]", "")

total_notes = sum(chapter[i]["num_notes"] for i in range(1,123))

print("Write HTML..")
os.makedirs("html", exist_ok=True)
books = {
    1: "<abbr title='Harry James Potter-Evans-Verres'>HJPEV</abbr> and the Methods of Rationality",
    22: "<abbr title='Harry James Potter-Evans-Verres'>HJPEV</abbr> and the Professor's Games",
    38: "<abbr title='Harry James Potter-Evans-Verres'>HJPEV</abbr> and the Shadows of Death",
    65: "<abbr title='Hermione Jean Granger'>HJG</abbr> and the Phoenix's Call",
    86: "<abbr title='Harry James Potter-Evans-Verres'>HJPEV</abbr> and the Last Enemy",
    100: "<abbr title='Harry James Potter-Evans-Verres'>HJPEV</abbr> and the Philosopher's Stone"
}
index = open("template/index.html","r").read()
toc = ""
for i in range(1,123):
    if i in books:
        if i != 1:
            toc += '</ul>'
        toc += f"<h2>{books[i]}</h2>"
        toc += '<ul class="toc">'
    toc += f'<li><a href="/chapter/{i}">'
    toc += chapter[i]["title"]
    toc += "</a>"
    if chapter[i]["num_notes"]:
        note_s = " note" if chapter[i]["num_notes"] == 1 else " notes"
        toc += f'<span class="num-notes"> [{chapter[i]["num_notes"]}{note_s}]</span>'
    toc += "</li>"
toc += "</ul>"
index = index.replace("[TOC]", toc)
index = index.replace("[TOTAL]", str(total_notes))
index = index.replace("[DATE]", datetime.date.today().strftime("%Y-%m-%d"))
out = open("html/index.html", "w", encoding='utf-8')
out.write(index)
out.close()

for i in trange(1,123):
    toc = ""
    for j in range(1,123):
        active = ' class="active-chapter"' if i == j else ""
        toc += f'<li{active}><a href="/chapter/{j}">'
        toc += chapter[j]["title"]
        toc += "</a>"
        if chapter[j]["num_notes"]:
            note_s = " note" if chapter[j]["num_notes"] == 1 else " notes"
            toc += f'<span class="num-notes"> [{chapter[j]["num_notes"]}{note_s}]</span>'
        toc += "</li>"
    htmls[i] = htmls[i].replace("[TOC]", toc)
    os.makedirs(f"html/chapter/{i}", exist_ok=True)
    out = open(f"html/chapter/{i}/index.html", "w", encoding='utf-8')
    out.write(htmls[i])
    out.close()

full = full.replace("[TOC]", toc)
out = open("html/full.html", "w", encoding='utf-8')
out.write(full)
out.close()

os.system("cp template/style.css html/style.css")

# if input("Format HTML? ") != "":
#     for filename in tqdm([str(i) for i in range(1,123)] + ["full", "index"]):
#         subprocess.Popen(['npx', 'prettier', '--parser', 'html', '--write', f'html/{filename}.html'])
