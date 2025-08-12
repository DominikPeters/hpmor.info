#!/usr/bin/env python3
"""
Generate HTML preview for a single chapter using the existing build.py script.
Usage: python generate_preview.py <paragraph_number> <issue_number>
"""

import sys
import os
import subprocess
import shutil
from ruamel.yaml import YAML

def find_chapter_for_paragraph(paragraph_number):
    """Find which chapter contains the given paragraph number."""
    yaml = YAML()
    for i in range(1, 123):
        try:
            with open(f"yaml/{i}.yaml", "r") as f:
                chapter = yaml.load(f)
            if paragraph_number in chapter:
                return i
        except FileNotFoundError:
            continue
    return None

def main():
    if len(sys.argv) != 3:
        print("Usage: python generate_preview.py <paragraph_number> <issue_number>")
        sys.exit(1)
        
    paragraph_number = int(sys.argv[1])
    issue_number = sys.argv[2]
    
    # Find the chapter containing this paragraph
    chapter_num = find_chapter_for_paragraph(paragraph_number)
    
    if chapter_num is None:
        print(f"Error: Could not find chapter containing paragraph {paragraph_number}")
        sys.exit(1)
    
    print(f"Generating preview for chapter {chapter_num}, paragraph {paragraph_number}")
    
    # Run the existing build script
    print("Running build.py...")
    subprocess.run(["python", "build.py"], check=True)
    
    # Create preview directory
    os.makedirs("preview", exist_ok=True)
    
    # Copy the specific chapter HTML and stylesheet
    shutil.copy(f"html/chapter/{chapter_num}/index.html", f"preview/{issue_number}.html")
    shutil.copy("html/style.css", "preview/style.css")
    
    # Add noindex meta tag to preview HTML
    preview_file = f"preview/{issue_number}.html"
    with open(preview_file, "r", encoding="utf-8") as f:
        html_content = f.read()
    
    # Insert noindex meta tag before closing </head> tag
    html_content = html_content.replace(
        "</head>", 
        '    <meta name="robots" content="noindex, nofollow">\n</head>'
    )
    
    with open(preview_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print(f"Preview generated at preview/{issue_number}.html")
    print(f"Chapter number: {chapter_num}")

if __name__ == "__main__":
    main()