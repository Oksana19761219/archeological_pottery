from django.contrib import admin
from .models import \
    Bibliography, \
    BibliographicReference, \
    PotteryLipForm, \
    PotteryOrnamentForm

# Register your models here.

admin.site.register(Bibliography)
admin.site.register(BibliographicReference)
admin.site.register(PotteryLipForm)
admin.site.register(PotteryOrnamentForm)