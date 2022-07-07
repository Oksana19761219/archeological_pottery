from django.shortcuts import render
from django.http import HttpResponse
from .models import \
    Bibliography, \
    BibliographicReference, \
    PotteryLipShape, \
    PotteryOrnamentShape, \
    PotteryDescription

def bibliography(request):
    reports = Bibliography.objects.all()
    reports_count = Bibliography.objects.all().count()
    context = {
        'reports': reports,
        'reports_count': reports_count
               }

    return render(request, 'bibliography.html', context=context)

