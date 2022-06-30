from django.contrib import admin
from .models import Bibliography, BibliographicReference

# Register your models here.

admin.site.register(Bibliography)
admin.site.register(BibliographicReference)