
import os,csv,re,nltk,PyPDF2

from google.cloud import translate
from operator import itemgetter
import numpy as np

from nltk.cluster.util import cosine_distance
from nltk.corpus import brown, stopwords

from djongo import models
from .models import Author
from django.shortcuts import render, redirect, reverse
from django.core.files.storage import FileSystemStorage
import django.db.models
from django.views.generic.base import TemplateView
# from django import forms
# from .forms import LeaseForm
# from .models import Lease
# Create your views here.
from django.http import HttpResponseRedirect

class HomePageView(TemplateView):

    template_name = 'home.html'

class UploadPageView(TemplateView):

    template_name = 'upload.html'
