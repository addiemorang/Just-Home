from django import forms
from django.forms import ModelForm
from .models import PDFModel

class PDFForm(ModelForm):
    class Meta:
        model = PDFModel
        fields = ['name','pdf',]
