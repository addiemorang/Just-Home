from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('', views.post_list, name='post_list')
]
