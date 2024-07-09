from django.shortcuts import render, redirect
from .forms import UploadPDFForm
from .utils import extract_text_from_pdf, summarize_text
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm


def upload_pdf(request):
    if request.method == 'POST':
        form = UploadPDFForm(request.POST, request.FILES)
        if form.is_valid():
            pdf = request.FILES['pdf']
            if not pdf.name.endswith('.pdf'):
                return render(request, 'paper_summarizer/upload.html', {'form': form, 'error': 'Please upload a valid PDF file.'})
            try:
                text = extract_text_from_pdf(pdf)
                summary = summarize_text(text)
                return render(request, 'paper_summarizer/result.html', {'summary': summary})
            except Exception as e:
                return render(request, 'paper_summarizer/upload.html', {'form': form, 'error': str(e)})
    else:
        form = UploadPDFForm()
    return render(request, 'paper_summarizer/upload.html', {'form': form})
