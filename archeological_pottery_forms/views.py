from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Q
from .models import \
    Bibliography, \
    BibliographicReference, \
    PotteryLipShape, \
    PotteryOrnamentShape, \
    PotteryDescription, \
    ResearchObject



def search(request):
    query = request.GET.get('query')
    # search_results = ResearchObject.objects.filter(Q(name__icontains=query))
    search_results = Bibliography.objects.filter(Q(author__icontains=query) | Q(title__icontains=query))


    context = {
        'reports': search_results,
        'query': query
    }
    return render(request,'search.html', context=context)




def bibliography(request):
    reports = Bibliography.objects.all()
    reports_count = Bibliography.objects.all().count()
    context = {
        'reports': reports,
        'reports_count': reports_count
               }

    return render(request, 'bibliography.html', context=context)

