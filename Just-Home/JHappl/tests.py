from django.test import TestCase
from JHappl.models import Author
# Create your tests here.

class TestAuthor(TestCase):

    def setup(self):
        sample = Author.objects.create(name='addie', email='sample@sample.com')
        sample.save()
