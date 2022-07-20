from django.http import HttpResponseRedirect
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
from .forms import \
    PotteryDescriptionForm, DrawingForm
from PIL import Image
from .my_models.read_drawings import \
    orthogonalize_image, \
    get_contour_coords, \
    flip_image


def index(request):
    return render(request, 'index.html')


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


@csrf_protect
def register(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']
        if password == password2:
            if User.objects.filter(username=username).exists():
                messages.error(request, f'Vartotojo vardas {username} užimtas!')
                return redirect('register')
            else:
                if User.objects.filter(email=email).exists():
                    messages.error(request, f'Vartotojas su el. paštu {email} jau užregistruotas!')
                    return redirect('register')
                else:
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


@csrf_protect
def object(request, object_id):
    single_object = get_object_or_404(ResearchObject, pk=object_id)
    reports = Bibliography.objects.filter(research_object__exact = object_id)
    context = {
        'object': single_object,
        'reports': reports,
    }
    if request.method == 'POST' and 'describe' in request.POST:
        return HttpResponseRedirect(reverse('describe', args=[object_id]))
    elif request.method == 'POST' and 'read_drawings' in request.POST:
        return HttpResponseRedirect(reverse('read_drawings', args=[object_id]))
    return render(request, 'object.html', context=context)


@csrf_protect
def get_pottery_description(request, object_id):
    if request.method == 'POST':
        form = PotteryDescriptionForm(request.POST)
        if form.is_valid():
            data = PotteryDescription(
                find_registration_nr=form.cleaned_data['find_registration_nr'],
                arc_length=form.cleaned_data['arc_length'],
                color=form.cleaned_data['color'],
                lip_id=form.cleaned_data['lip_id'],
                ornament_id=form.cleaned_data['ornament_id'],
                note=form.cleaned_data['note'],
                research_object_id=object_id
            )
            data.save()
            form = PotteryDescriptionForm()
    else:
        form = PotteryDescriptionForm()
    return render(request, 'describe.html', {'form': form})




@csrf_protect
def read_drawings(request, object_id):
    if request.method == 'POST':
        form = DrawingForm(request.POST, request.FILES)
        if form.is_valid():
            files = request.FILES.getlist('drawing')
            frame_width = int(request.POST['frame_width'])
            frame_height = int(request.POST['frame_height'])
            frame_color = request.POST['frame_color']
            ceramic_color = request.POST['ceramic_color']
            ceramic_orientation = request.POST['ceramic_orientation']

            if files and frame_width>0 and frame_height>0:
                for file in files:
                    file_name = str(file).split('.')[0]
                    image = Image.open(file)
                    flipped_image = flip_image(image, ceramic_orientation)
                    ortho_image = orthogonalize_image(flipped_image, frame_color, frame_width, frame_height)
                    # ortho_image.show()
                    contour_coords = get_contour_coords(ortho_image, ceramic_color, frame_color)
                    print(contour_coords)
        form = DrawingForm()
    else:
        form = DrawingForm()
    return render(request, 'read_drawings.html', {'form': form} )



