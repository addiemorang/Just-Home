
from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from django import forms
from .forms import LeaseForm
from .models import Lease
# Create your views here.
from django.http import HttpResponse

def home(request):
    if request.method == 'POST' and request.FILES['myfile']:
        myfile = request.FILES['myfile']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)
        return render(request, 'lease_interpreter/home.html', {
            'uploaded_file_url': uploaded_file_url
        })
    return render(request, 'lease_interpreter/home.html')

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
    leases = Lease.objects.all()
    return render(request, 'lease_interpreter/lease_list.html', {
        'leases': leases
    })


def upload_lease(request):
    if request.method =="POST":
        form = LeaseForm(request.FILES['myfile'])
        if form.is_valid():
            form.save()
            return redirect('leases/list')
    else:
        form = LeaseForm()
    return render(request, 'lease_interpreter/upload_lease.html', {
        'form': form
    })

