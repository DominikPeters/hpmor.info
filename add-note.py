import sys
from ruamel.yaml import YAML
from datetime import datetime

def parse_issue(issue_body):
    lines = issue_body.split('\n')
    paragraph_number = None
    author = None
    text = None
    for line in lines:
        if line.startswith('### Paragraph Number'):
            paragraph_number = int(line.split(':')[1].strip())
        elif line.startswith('### Author'):
            author = line.split(':')[1].strip()
        elif line.startswith('### Text'):
            text = line.split(':', 1)[1].strip()
    return paragraph_number, author, text

def add_note_to_yaml(paragraph_number, author, text, branch_name, issue_date):
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
                'text': text
            })
            with open(f"yaml/{i}.yaml", "w") as f:
                yaml.dump(chapter, f)
            break

if __name__ == "__main__":
    issue_body = sys.argv[1]
    branch_name = sys.argv[2]
    issue_date = datetime.strptime(sys.argv[3], "%Y-%m-%d").strftime("%Y/%m/%d")
    paragraph_number, author, text = parse_issue(issue_body)
    add_note_to_yaml(paragraph_number, author, text, branch_name, issue_date)
