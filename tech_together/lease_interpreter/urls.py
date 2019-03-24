from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.upload, name='upload'),
    path('/home#resume', views.home, name='home#resume'),
    path('home', views.home, name='home'),
    path('leases/list', views.lease_list, name='lease_list'),
    path('leases/upload', views.upload_lease, name='upload_lease')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
