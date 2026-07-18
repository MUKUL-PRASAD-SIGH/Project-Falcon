import re
import glob
import os

def clean_markdown(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
        
    original_text = text

    # Remove escapes
    text = text.replace('\*\*', '**')
    text = text.replace('\-', '-')
    text = text.replace('\>', '>')
    text = text.replace('\---', '---')
    text = text.replace('\`', '`')
    text = text.replace('\_', '_')
    text = text.replace('\[', '[')
    text = text.replace('\]', ']')

    # Fix spacing in tables
    text = re.sub(r'\n\n\|', '\n|', text)

    # Fix spacing in lists
    text = re.sub(r'\n\n- ', '\n- ', text)
    text = re.sub(r'\n\n> - ', '\n> - ', text)
    text = re.sub(r'\n\n> ', '\n> ', text)

    # Fix spacing around headers
    text = re.sub(r'\n(#+) ', r'\n\n\1 ', text)

    # Remove extra blank lines
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = text.strip() + '\n'

    if text != original_text:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"Cleaned {filepath}")
    else:
        print(f"Skipped {filepath} (no changes)")

# Target all markdown files in docs
for file in glob.glob('docs/*.md'):
    clean_markdown(file)
