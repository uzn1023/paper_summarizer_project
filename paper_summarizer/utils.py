import fitz  # PyMuPDF
from .llm import get_summarize_by_format_from_text
import time

def extract_text_from_pdf(pdf_file):
    document = fitz.open(pdf_file, filetype="pdf")
    text = ""
    for page_num in range(len(document)):
        page = document.load_page(page_num)
        text += page.get_text()
        with open("text.txt", 'w', encoding="utf-8") as f:
            print(text, file=f)
    return text

def summarize_text(text, GEMINI_API_KEY, max_retries=5):
    retries = 0
    while retries < max_retries:
        if len(text) < 100:
            return "The text is too short to summarize."
        try:
            summary = get_summarize_by_format_from_text(text, GEMINI_API_KEY)
            if summary:
                return summary
            else:
                retries += 1
                time.sleep(10)  # Wait for 1 second before retrying
        except ValueError as e:
            print(e)
            retries += 1
            time.sleep(10)  # Wait for 1 second before retrying
    return "Summarization failed after multiple retries. Please check the content of the PDF."
