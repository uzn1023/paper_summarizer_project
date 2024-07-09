from django import forms

class UploadPDFForm(forms.Form):
    pdf = forms.FileField()
