
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from django import forms
from .forms import LeaseForm
# Create your views here.
from django.http import HttpResponse

def upload(request):
     if request.method == 'POST' and request.FILES['myfile']:
        myfile = request.FILES['myfile']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)
        return render(request, 'lease_interpreter/upload.html', {
            'uploaded_file_url': uploaded_file_url
        })
     return render(request, 'lease_interpreter/upload.html')

def lease_list(request):
    return render(request, 'lease_list.html')


def upload_lease(request):
    return render(request, 'upload_lease.html', {
        'form': form
    })