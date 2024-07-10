from django.shortcuts import render
from .forms import UploadPDFForm
from .utils import extract_text_from_pdf, summarize_text
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from .forms import SignUpForm
from django.views.generic import TemplateView
from .forms import activate_user

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