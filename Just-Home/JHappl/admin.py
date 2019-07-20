from django.contrib import admin

from .models import PDFModel, RawTextModel
# from .models import Lease

# admin.site.register(Question)
# admin.site.register(Question2)
# admin.site.register(Post)
admin.site.register(PDFModel)
admin.site.register(RawTextModel)
