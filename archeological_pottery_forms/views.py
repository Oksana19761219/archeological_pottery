from django.shortcuts import render, get_object_or_404
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
    query_words =query.split(' ')
    reports = Bibliography.objects.all()
    for word in query_words:
        search_results = reports.filter(
            Q(author__icontains=word) |
            Q(title__icontains=word) |
            Q(report_year__icontains=word)
        )
        reports = search_results


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

def object(request, object_id):
    single_object = get_object_or_404(ResearchObject, pk=object_id)
    reports = Bibliography.objects.filter(research_object__exact = object_id)
    context = {
        'object': single_object,
        'reports': reports,
    }
    return render(request, 'object.html', context=context)