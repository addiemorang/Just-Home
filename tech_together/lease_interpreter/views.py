from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse


def index(request):
    return HttpResponse("Hello, world. You're at the lease_interpreter index.")


def post_list(request):
    return render(request, 'blog/post_list.html', {})
