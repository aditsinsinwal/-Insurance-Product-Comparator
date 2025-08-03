Insurance Product Comparator
The Insurance Product Comparator is a Flask-based web application that uses OCR and Large Language Models (LLMs) to extract and compare key information from two scanned life or health insurance plan documents in PDF format.

It highlights differences in:
-Coverage Details
-Exclusions
-Premium Structures
-Waiting Periods
-Age Eligibility


Built for Scanned PDFs
Unlike apps that require machine-readable PDFs, this tool is OCR-first — it converts scanned images to text using Tesseract, then applies AI to understand and summarize the documents.

Features
-OCR support for scanned insurance PDFs (via pytesseract)
-Structured field extraction using OpenAI GPT-4
-Side-by-side comparison of insurance plans
-Keyword filtering to reject irrelevant documents
-Simple web interface made using (Flask + HTML + CSS)
-Upload and compare locally — no database required for backend
