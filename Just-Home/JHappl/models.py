from django.conf import settings
from django.db import models
from django.utils import timezone
# Create your models here.

class PDFModel(models.Model):
    name = models.CharField(max_length=10, default='0')
    pdf = models.FileField()

    @classmethod
    def get_PDF(self):
        return self.pdf

class RawTextModel(models.Model):
    name = models.CharField(max_length=10, default='sample')
    text = models.TextField()
