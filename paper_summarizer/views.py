from django.shortcuts import render
from .forms import UploadPDFForm, URLForm
from .utils import extract_text_from_pdf, summarize_text
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from .forms import SignUpForm
from django.views.generic import TemplateView
from .forms import activate_user
from .add_notion import  add_notion
import requests
import tempfile

def upload_pdf(request):
    if request.method == 'POST':
        form = UploadPDFForm(request.POST, request.FILES)
        if form.is_valid():
            pdf = request.FILES['pdf']
            # 一時ファイルを作成
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                temp_file.write(pdf.read())
                if not pdf.name.endswith('.pdf'):
                    return render(request, 'paper_summarizer/upload_pdf.html', {'form': form, 'error': 'Please upload a valid PDF file.'})
                try:
                    text = extract_text_from_pdf(temp_file.name)
                    summary = summarize_text(text, request.user.GeminiAPI)
                    try:
                        add_notion(summary, request.user.NotionDatabaseID, request.user.NotionAPI)
                    except Exception as e:
                        print(e.args)
                    return render(request, 'paper_summarizer/result.html', {'summary': summary})
                except Exception as e:
                    return render(request, 'paper_summarizer/upload_pdf.html', {'form': form, 'error': str(e)})
    else:
        form = UploadPDFForm()
    return render(request, 'paper_summarizer/upload_pdf.html', {'form': form})

def upload_url(request):
    form = URLForm(request.POST, request.FILES)
    if request.method == 'POST':
        pdf_url = request.POST.get("url")
        try:
            response = requests.get(pdf_url)
            if response.status_code == 200:
                # 一時ファイルを作成
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                    temp_file.write(response.content)
                    text = extract_text_from_pdf(temp_file.name)
                    summary = summarize_text(text, request.user.GeminiAPI)
                    try:
                        add_notion(summary, request.user.NotionDatabaseID, request.user.NotionAPI)
                    except Exception as e:
                        print(e.args)
                    return render(request, 'paper_summarizer/result.html', {'summary': summary})
            else:
                return render(request, 'paper_summarizer/upload_url.html', {'form': form, 'error': 'Failed to fetch PDF from the provided URL.'})
        except Exception as e:
            return render(request, 'paper_summarizer/upload_url.html', {'form': form, 'error': str(e)})        
    return render(request, 'paper_summarizer/upload_url.html', {'form': form})

class SignUpView(CreateView):
    form_class = SignUpForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'

class ActivateView(TemplateView):
    template_name = "registration/activate.html"
    
    def get(self, request, uidb64, token, *args, **kwargs):
        # 認証トークンを検証して、
        result = activate_user(uidb64, token)
        # コンテクストのresultにTrue/Falseの結果を渡します。
        return super().get(request, result=result, **kwargs)