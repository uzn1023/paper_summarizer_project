import fitz  # PyMuPDF
from .llm import get_summarize_by_format_from_text

def extract_text_from_pdf(pdf_file):
    document = fitz.open(stream=pdf_file.read(), filetype="pdf")
    text = ""
    for page_num in range(len(document)):
        page = document.load_page(page_num)
        text += page.get_text()
        with open("text.txt", 'w', encoding="utf-8") as f:
            print(text, file=f)
    return text

def summarize_text(text, GEMINI_API_KEY):
    if len(text) < 100:
        return "The text is too short to summarize."
    try:
        summary = get_summarize_by_format_from_text(text, GEMINI_API_KEY)
        return summary if summary else "Summarization failed. Please check the content of the PDF."
    except ValueError:
        return "Summarization failed. Please check the content of the PDF."
