# New version, June 2021
# Builds HTML files & uploads to server
# does not connect to reddit api, just reads local json files

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

vscode_prefix = "https://github.dev/DominikPeters/hpmor.info/blob/master/yaml/"
PRINT_VSCODE_LINKS = True
vscode_link = {}

comment_ids = set()
for i in trange(1, 123):
    with open("yaml/"+str(i)+".yaml", "r") as f:
        chapter[i] = yaml.load(f)
        chapter[i]["num_notes"] = 0
    # make vscode deeplinks for paragraphs
    with open("yaml/"+str(i)+".yaml", "r") as f:
        for lineno, line in enumerate(f):
            if not line:
                continue
            line = line.strip()
            if line[0] != " " and line[-1] == ":":
                number = line[:-1]
                if number.isdigit():
                    vscode_link[int(number)] = vscode_prefix + str(i) + ".yaml#L" + str(lineno+1)
                    if int(number) - 1 in vscode_link:
                        vscode_link[int(number) - 1] += f"-L{lineno}"

def note2string(note):
    if note["type"] == "reddit":
        html = '<div class="note">'
        if "score" in note:
            points = str(note["score"]) + (" point" if note["score"] == 1 else " points") + ' '
        else:
            points = ""
        html += '<span class="meta"><a href="' + note["url"] +'"><b>'+note["author"]+'</b> '+ points + note["date"] +'</a></span>'
        html += note["text"]
        if "replies" in note:
            for child in note["replies"]:
                html += note2string(child)
        html += "</div>"
    elif note["type"] == "original":
        html = '<div class="note">' + note["text"] + '</div>'
    else:
        raise Exception("Unknown note type:" + note["type"])
    return html

# generate html
print("Generate HTML..")
header = open("template/header.html","r").read()
footer = open("template/footer.html","r").read()
# full book html
full = header.replace("[NR]", "1&ndash;122").replace("[TITLE]", "Harry Potter and the Methods of Rationality")
full = full.replace("[CHAPTERLINKS]", "<div class='chapter-context-nav'><span class='go-home'><a href='/'>Home</a></span></div>").replace("[HEAD]", "").replace("[FIRST_NOTE_LINK]", "")
htmls = {}
for i in trange(1, 123):
    html = header.replace("[NR]", str(i)).replace("[TITLE]", chapter[i]["title"])
    head = ""
    chapterlinks = "<div class='chapter-context-nav'>"
    if i != 1:
        chapterlinks += '<span class="prev-chapter"><a href="'+str(i-1)+'.html">&larr; '+str(i-1)+'</a></span>'
        head += '<link rel="prerender" href="'+str(i-1)+'.html">'
    chapterlinks += '<span class="go-home"><a href="/">Home</a></span>'
    if i != 122:
        chapterlinks += '<span class="next-chapter"><a href="'+str(i+1)+'.html">'+str(i+1)+' &rarr;</a></span>'
        head += '<link rel="prerender" href="'+str(i+1)+'.html">'
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
        html = html.replace("[FIRST_NOTE_LINK]", '<div id="jump-to-first-note"><a href="#'+str(active_paras[0])+'">first note &darr;</a></div>')
    else:
        html = html.replace("[FIRST_NOTE_LINK]", "")
    boilerplate = html
    html = ""
    full += "<h2>" + chapter[i]["title"] + "</h2>"
    interesting_paras = set(para for para in chapter_paras if any(para+offset in active_paras for offset in [-3,-2,-1,0,1,2]) \
                                or (para-4 in active_paras and sum(len(chapter[i][para+offset]["text"]) for offset in [-4,-3,-2,-1]) < 200))
    for para in chapter_paras:
        if para in interesting_paras and (para-1) not in interesting_paras and para not in active_paras:
            html += '<div class="expand-button"><a href="#'+str(para)+'" onclick="expand()">+</a></div>'
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
                    html += '<div class="jump-to-prev-note"><a href="#'+str(prev-2)+'">&uarr;</a></div>'
            for note in chapter[i][para]["notes"]:
                chapter[i]["num_notes"] += 1
                html += note2string(note)
            if para != active_paras[-1]:
                following = active_paras[active_paras.index(para) + 1]
                if following > para + 2 and following - 2 < chapter[i]["last_para"]:
                    html += '<div class="jump-to-next-note"><a href="#'+str(following-2)+'">&darr;</a></div>'
            html += "</div>"
        else:
            pass
            # html += '<div class="notes no-notes"><a>annotate on reddit</a></div>'
        html += '\n<p>\n<a id="' + str(para) + '"></a>'
        # old version with links to reddit
        # html += '<span class="para-number"><a href="javascript:showCommentField(' + str(para) + ')" class="para-anchor">+</a> <a href="https://www.reddit.com/r/hpmor_annotated/comments/' + str(chapter[i]["reddit_posts"][-1]) + '/" class="para-anchor">&#9741;</a> '+str(para)+' '
        html += '<span class="para-number">'+str(para)+' '
        html += '<a href="#' + str(para) + '" class="para-anchor">&para;</a> \n'
        if PRINT_VSCODE_LINKS:
            html += '<a href="' + vscode_link[para] + '" class="para-anchor">+</a> \n'
        html += '</span>\n'
        html += chapter[i][para]["text"]
        # html += ' <a href="javascript:showCommentField(' + str(para) + ')" class="comment-shower">+</a>'
        html += "\n</p>"
        # add comment field
        # html += "<div class='comment-field' id='comment-"+str(para)+"'><textarea id='textarea-"+str(para)+"' rows='4' cols='60'>"+str(para)+"</textarea><button id='submit-"+str(para)+"' onclick='javascript:submitComment("+str(para)+")'>Submit</button><div id='response-"+str(para)+"'></div></div>"
        html += "\n</div>"
        if interesting_paras and para == max(interesting_paras):
            html += '<div class="expand-button" id="last-expand-button"><a href="#'+str(para)+'" onclick="expand()">+</a></div>'
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
        toc += "<h2>"+ books[i] +"</h2>"
        toc += '<ul class="toc">'
    toc += '<li><a href="'+str(i)+'.html">'
    toc += chapter[i]["title"]
    toc += "</a>"
    if chapter[i]["num_notes"]:
        note_s = " note" if chapter[i]["num_notes"] == 1 else " notes"
        toc += '<span class="num-notes"> ['+str(chapter[i]["num_notes"])+note_s+']</span>'
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
        toc += '<li'+active+'><a href="'+str(j)+'.html">'
        toc += chapter[j]["title"]
        toc += "</a>"
        if chapter[j]["num_notes"]:
            note_s = " note" if chapter[j]["num_notes"] == 1 else " notes"
            toc += '<span class="num-notes"> ['+str(chapter[j]["num_notes"])+note_s+']</span>'
        toc += "</li>"
    htmls[i] = htmls[i].replace("[TOC]", toc)
    out = open("html/"+str(i)+".html", "w", encoding='utf-8')
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
    
if PRINT_VSCODE_LINKS or input("Upload to server? ") == "":
    sys.exit()

# upload via FTP
print("FTP upload..")
ftp = FTP(os.environ["FTP_SERVER"])
ftp.login(os.environ["FTP_USER"], os.environ["FTP_PASS"])
try:
    ftp.storbinary('STOR style.css', open("template/style.css", "rb")) 
    ftp.storbinary('STOR index.html', open("html/index.html", "rb"))
    for i in trange(1, 123):
        ftp.storbinary('STOR '+str(i)+'.html', open("html/"+str(i)+".html", "rb")) 
finally:
    ftp.quit() 

print("Done.")