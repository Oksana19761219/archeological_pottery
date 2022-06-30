from django.contrib import admin
from .models import \
    Bibliography, \
    BibliographicReference, \
    PotteryLipShape, \
    PotteryOrnamentShape

# Register your models here.

admin.site.register(Bibliography)
admin.site.register(BibliographicReference)
admin.site.register(PotteryLipShape)
admin.site.register(PotteryOrnamentShape)