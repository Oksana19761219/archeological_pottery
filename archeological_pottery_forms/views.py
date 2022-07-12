from django.shortcuts import render, get_object_or_404, reverse, redirect
from django.contrib import messages
from django.contrib.auth.forms import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.csrf import csrf_protect
from django.views.generic import CreateView
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


@csrf_protect
def register(request):
    if request.method == "POST":
        # pasiimame reikšmes iš registracijos formos
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']
        # tikriname, ar sutampa slaptažodžiai
        if password == password2:
            # tikriname, ar neužimtas username
            if User.objects.filter(username=username).exists():
                messages.error(request, f'Vartotojo vardas {username} užimtas!')
                return redirect('register')
            else:
                # tikriname, ar nėra tokio pat email
                if User.objects.filter(email=email).exists():
                    messages.error(request, f'Vartotojas su el. paštu {email} jau užregistruotas!')
                    return redirect('register')
                else:
                    # jeigu viskas tvarkoje, sukuriame naują vartotoją
                    User.objects.create_user(username=username, email=email, password=password)
        else:
            messages.error(request, 'Slaptažodžiai nesutampa!')
            return redirect('register')
    return render(request, 'register.html')


class UserPotteryListView(LoginRequiredMixin,generic.ListView):
    model = PotteryDescription
    template_name = 'user_pottery_description.html'

    def get_queryset(self):
        return PotteryDescription.objects.filter(researcher=self.request.user)




# class PotteryDescriptionView(FormMixin, generic.DetailView):
#     model = PotteryDescription
#     template_name = 'object.html'
#     form_class = PotteryDescriptionForm
#
#     def get_success_url(self):
#         return reverse('object', kwargs={'pk': self.object.id})
#
#     def post(self, request, *args, **kwargs):
#         self.object = self.get_object()
#         form = self.get_form()
#         if form.is_valid():
#             return self.form_valid(form)
#         else:
#             return self.form_invalid(form)
#
#     def form_valid(self, form):
#         form.instance.research_object = self.object
#         # form.save()
#         # print('ok')
#         return super(PotteryDescriptionView, self).form_valid(form)

# class PotteryDescriptionCreateView(LoginRequiredMixin, CreateView):
#     model = PotteryDescription
#     fields = [
#         'find_registration_nr',
#         'arc_length',
#         'color',
#         'lip',
#         'ornament',
#         'note',
#         'research_object'
#     ]
#     success_url = '/pottery/object/'
#     template_name = 'object.html'
#
#     def form_valid(self, form):
#         form.instance.reader = self.request.user
#         return super().form_valid(form)

