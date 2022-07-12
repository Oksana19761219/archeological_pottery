from django.shortcuts import render, get_object_or_404, reverse
from django.http import HttpResponse
from django.db.models import Q
from django.views import generic
from django.views.generic.edit import FormMixin
from .models import \
    Bibliography, \
    BibliographicReference, \
    PotteryLipShape, \
    PotteryOrnamentShape, \
    PotteryDescription, \
    ResearchObject
from .forms import PotteryDescriptionForm



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


class PotteryDescriptionView(FormMixin, generic.DetailView):
    model = PotteryDescription
    template_name = 'object.html'
    form_class = PotteryDescriptionForm

    def get_success_url(self):
        return reverse('object', kwargs={'pk': self.object.id})

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        form.instance.research_object = self.object
        # form.save()
        print('ok')
        return super(PotteryDescriptionView, self).form_valid(form)