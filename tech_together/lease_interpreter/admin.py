from django.contrib import admin
from .models import Question
from .models import Question2
from .models import Post
from .models import Lease
# Register your models here.

admin.site.register(Question)
admin.site.register(Question2)
admin.site.register(Post)
admin.site.register(Lease)
