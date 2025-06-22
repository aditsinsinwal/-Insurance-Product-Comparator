import re

def clean_ocr_text(text):
    # Remove long blank lines or repetitive headers/footers
    text = re.sub(r'\n{2,}', '\n', text)
    text = re.sub(r'Page \\d+ of \\d+', '', text)
    return text.strip()
