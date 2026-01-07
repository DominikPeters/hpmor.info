#!/usr/bin/env python3
import os
import yaml
from pathlib import Path

yaml_dir = Path('yaml')

# Process all YAML files in order (1-122)
for chapter_num in range(1, 123):
    yaml_file = yaml_dir / f'{chapter_num}.yaml'
    if not yaml_file.exists():
        continue
    with open(yaml_file, 'r', encoding='utf-8') as f:
        content = f.read()

    data = yaml.safe_load(content)

    if data is None:
        continue

    # Iterate through paragraphs
    for para_num, para_content in data.items():
        if isinstance(para_content, dict) and 'notes' in para_content:
            # Extract the YAML for this paragraph from the file
            lines = content.split('\n')
            in_paragraph = False
            paragraph_lines = []
            indent_level = None

            for i, line in enumerate(lines):
                # Check if we found the paragraph
                if line.strip().startswith(f"{para_num}:"):
                    in_paragraph = True
                    indent_level = len(line) - len(line.lstrip())
                    paragraph_lines.append(line)
                elif in_paragraph:
                    # Check if we've reached the next paragraph
                    if line and not line[0].isspace():
                        break
                    if line.strip() and len(line) - len(line.lstrip()) == indent_level:
                        # Next paragraph at same level
                        break
                    paragraph_lines.append(line)

            print(f"{'='*80}")
            print(f"File: {yaml_file.name} | Paragraph {para_num}")
            print(f"{'='*80}")
            print('\n'.join(paragraph_lines))
            print()
