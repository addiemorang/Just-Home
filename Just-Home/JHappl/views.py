from django.shortcuts import render, redirect, reverse
from django.core.files.storage import FileSystemStorage
import django.db.models
from django.views.generic.base import TemplateView
from django.http import HttpResponseRedirect
from .forms import PDFForm
from .models import PDFModel, RawTextModel
import os
import PyPDF2
import nltk

# Create your views here.

class HomePageView(TemplateView):
    template_name = 'home.html'


class UploadPageView(TemplateView):
    template_name = 'upload.html'

    def post(self, request, *args, **kwargs):
        if request.method == 'POST' and request.FILES['myfile']:
            file = request.FILES['myfile']
            p = PDFModel(name=file.name, pdf = file)
            p.save()
            return HttpResponseRedirect('/success')
        else:
            print("error")
        return render(request, 'upload.html', {'form': form})


class SuccessPageView(TemplateView):
    template_name = 'success.html'

class FailurePageView(TemplateView):
    template_name = 'failure.html'


def get_text_from_lease(pdf_name):
    pdf = open(pdf_name, 'rb')
    pdf_reader = PyPDF2.PdfFileReader(pdf)
    num_pages = pdf_reader.numPages
    lease_text = ''
    for i in range(num_pages):
        lease_text += pdf_reader.getPage(i).extractText().replace('lessor', 'landlord').replace(
            'Lessor', 'landlord').replace('lessee', 'tenant').replace('Lessee', 'tenant')
    sentence_list = split_sentences(lease_text)
    return ' '.join(sentence_list)

def split_sentences(text):
    text = text.replace('™', '')
    text = text.replace('.', '. ')
    sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
    sentences = sent_detector.tokenize(text.strip().replace('\n', ''))
    return sentences
