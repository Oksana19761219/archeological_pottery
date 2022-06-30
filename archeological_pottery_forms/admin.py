from django.contrib import admin
from .models import \
    Bibliography, \
    BibliographicReference, \
    PotteryLipShape, \
    PotteryOrnamentShape, \
    PotteryDescription

# Register your models here.

admin.site.register(Bibliography)
admin.site.register(BibliographicReference)
admin.site.register(PotteryLipShape)
admin.site.register(PotteryOrnamentShape)
admin.site.register(PotteryDescription)