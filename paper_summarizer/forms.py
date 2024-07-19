from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.conf import settings

class URLForm(forms.Form):
    url = forms.CharField(label='URL', max_length=100)

class UploadPDFForm(forms.Form):
    pdf = forms.FileField(
        label='PDFファイル',
        help_text='アップロードするPDFファイルを選択してください。',
        widget=forms.FileInput(attrs={'accept': 'application/pdf'})
    )

User = get_user_model()

class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "email", "GeminiAPI", "NotionAPI", "NotionDatabaseID", "password1", "password2")
    
    @staticmethod
    def get_activate_url(user):
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        protocol = 'https' if not settings.DEBUG else 'http'
        return f"{protocol}://{settings.ALLOWED_HOSTS[1]}:8000/activate/{uid}/{token}/"

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.is_active = False
        
        if commit:
            user.save()
            subject = "PaperSummarizer登録確認メール"
            message_template = """
            ご登録ありがとうございます。
            以下URLをクリックして登録を完了してください。

            """
            activate_url = self.get_activate_url(user)
            message = message_template + activate_url
            user.email_user(subject, message)
        return user

def activate_user(uidb64, token):    
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except Exception:
        return False

    if default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return True
    
    return False