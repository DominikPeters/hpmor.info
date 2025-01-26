import sys
from ruamel.yaml import YAML
from ruamel.yaml.scalarstring import LiteralScalarString
from datetime import datetime

def parse_issue(issue_body):
    lines = issue_body.split('\n')
    paragraph_number = None
    author = None
    text = None
    
    current_section = None
    text_lines = []
    
    for line in lines:
        line = line.strip()
        if line.startswith('### '):
            current_section = line[4:]
        elif line and current_section:
            if current_section == 'Paragraph Number':
                paragraph_number = int(line)
            elif current_section == 'Author':
                author = line
            elif current_section == 'Text':
                text_lines.append(line)
    
    text = '\n'.join(text_lines).strip()
    return paragraph_number, author, text
    

def add_note_to_yaml(paragraph_number, author, text, issue_date, origin):
    yaml = YAML()
    for i in range(1, 123):
        with open(f"yaml/{i}.yaml", "r") as f:
            chapter = yaml.load(f)
        if paragraph_number in chapter:
            if 'notes' not in chapter[paragraph_number]:
                chapter[paragraph_number]['notes'] = []
            chapter[paragraph_number]['notes'].append({
                'type': 'original',
                'date': issue_date,
                'author': author,
                'origin': origin,
                'text': LiteralScalarString(text)
            })
            with open(f"yaml/{i}.yaml", "w") as f:
                yaml.dump(chapter, f)
            break

if __name__ == "__main__":
    issue_body = sys.argv[1]
    issue_date = datetime.strptime(sys.argv[2], "%Y-%m-%d").strftime("%Y/%m/%d")
    paragraph_number, author, text = parse_issue(issue_body)
    if author == "_No response_":
        author = ""
    origin = sys.argv[3]
    add_note_to_yaml(paragraph_number, author, text, issue_date, origin)
