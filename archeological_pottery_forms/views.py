from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, reverse, redirect
from django.contrib import messages
from django.contrib.auth.forms import User
from django.views.decorators.csrf import csrf_protect
from django.db.models import Q
from .models import \
    Bibliography, \
    PotteryDescription, \
    ResearchObject, \
    CeramicContour
from .forms import \
    PotteryDescriptionForm, DrawingForm
from PIL import Image
from .my_models.read_drawings import read_image_data


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


def _get_ceramic_id(file, object_id):
    file_name = str(file).split('.')[0]
    finds = PotteryDescription.objects.all()
    queryset = finds.filter(
        Q(find_registration_nr__exact=file_name) &
        Q(research_object__exact=object_id)
    )
    find_id = []
    for item in queryset:
        find_id.append(item.id)
    if len(find_id) == 1:
        return find_id[0]
    print('klaida, dubliuojasi radinių duomenys')
    return None


def _write_coordinates_to_model(coordinates):
    """How to write a Pandas Dataframe to Django model
    https://newbedev.com/how-to-write-a-pandas-dataframe-to-django-model"""
    if not coordinates.empty:
        df_records = coordinates.to_dict('records')
        model_instances = [CeramicContour(
            x=record['x'],
            y=record['y'],
            find_id=record['find']
        ) for record in df_records]
        CeramicContour.objects.bulk_create(model_instances)


def _vectorize_files_to_model(
        files,
        frame_width,
        frame_height,
        object_id,
        ceramic_color,
        frame_color,
        ceramic_orientation
):
    if files and frame_width > 0 and frame_height > 0:
        for file in files:
            ceramic_id = _get_ceramic_id(file, object_id)
            contour_coords = read_image_data(
                file,
                ceramic_id,
                ceramic_color,
                frame_color,
                frame_width,
                frame_height,
                ceramic_orientation
            )
            _write_coordinates_to_model(contour_coords)


@csrf_protect
def vectorize_drawings(request, object_id):
    if request.method == 'POST':
        form = DrawingForm(request.POST, request.FILES)
        if form.is_valid():
            files = request.FILES.getlist('drawing')
            frame_width = int(request.POST['frame_width'])
            frame_height = int(request.POST['frame_height'])
            frame_color = request.POST['frame_color']
            ceramic_color = request.POST['ceramic_color']
            ceramic_orientation = request.POST['ceramic_orientation']
            _vectorize_files_to_model(
                files,
                frame_width,
                frame_height,
                object_id,
                ceramic_color,
                frame_color,
                ceramic_orientation
            )
        form = DrawingForm()
    else:
        form = DrawingForm()
    return render(request, 'read_drawings.html', {'form': form})


@csrf_protect
def show_ceramic_profiles(request):
    queryset = CeramicContour.objects.values_list('find_id').distinct()
    ceramic_vectorized = PotteryDescription.objects.filter(pk__in=queryset)
    coordinates = None

    if request.method == 'POST':
        ceramic_id = int(request.POST['my_ceramic'])
        coordinates = CeramicContour.objects.filter(find_id=ceramic_id)

    context = {
        'my_ceramic': ceramic_vectorized,
        'coordinates': coordinates
    }
    return render(request, 'my_ceramic.html', context=context)
