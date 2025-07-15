from flask import Flask, render_template, request
import os
from extractor import extract_text_with_ocr
from comparator import extract_fields, compare_documents
import nltk
from nltk.tokenize import word_tokenize

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

nltk.download('punkt')

def check_keywords(text):
    tokens = word_tokenize(text.lower())
    must_have = {"coverage", "premium", "claim", "exclusion"}
    return any(word in tokens for word in must_have)

@app.route('/', methods=['GET', 'POST'])

def index():
    comparison_result = ""
    warning_message = ""

    if request.method == 'POST':
        files = request.files.getlist('pdfs')

        if len(files) != 2:
            warning_message = "Please upload exactly two scanned insurance PDFs."
        else:
            paths = []
            for file in files:
                path = os.path.join(UPLOAD_FOLDER, file.filename)
                file.save(path)
                paths.append(path)

            text_A = extract_text_with_ocr(paths[0])
            text_B = extract_text_with_ocr(paths[1])

            if not (check_keywords(text_A) and check_keywords(text_B)):
                warning_message = "Warning: One or both PDFs may not contain relevant insurance content."

            info_A = extract_fields(text_A)
            info_B = extract_fields(text_B)

            comparison_result = compare_documents(info_A, info_B)

    return render_template('index.html', result=comparison_result, warning=warning_message)

if __name__ == '__main__':
    app.run(debug=True)

from review_scraper import scrape_trustpilot_reviews
from review_analyzer import analyze_reviews

insurer_a_name = request.form.get("insurerA")
insurer_b_name = request.form.get("insurerB")

reviews_a = scrape_trustpilot_reviews(insurer_a_name)
reviews_b = scrape_trustpilot_reviews(insurer_b_name)

sentiment_a = analyze_reviews(insurer_a_name, reviews_a)
sentiment_b = analyze_reviews(insurer_b_name, reviews_b)

