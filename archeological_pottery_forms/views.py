from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, reverse, redirect
from django.contrib import messages
from django.contrib.auth.forms import User
from django.views.decorators.csrf import csrf_protect
from django.db.models import Q
from .models import Bibliography, \
                    PotteryDescription, \
                    ResearchObject, \
                    CeramicContour
from .forms import PotteryDescriptionForm, DrawingForm
from .my_models.vectorize_files import vectorize_files
from .my_models.messages import messages
import logging

logger = logging.getLogger(__name__)


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
    reports = Bibliography.objects.filter(research_object = object_id)

    vectors_queryset = CeramicContour.objects.values_list('find_id').distinct()
    vectors_id = [item[0] for item in vectors_queryset]
    this_object_vectors = PotteryDescription.objects\
        .filter(Q(research_object = object_id) & Q(pk__in=vectors_id))\
        .order_by('find_registration_nr')

    context = {
        'object': single_object,
        'reports': reports,
        'vectors': this_object_vectors
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
def review_ceramic_profiles(request):
    queryset = CeramicContour.objects.values_list('find_id').distinct()
    ceramic_vectors = PotteryDescription.objects.filter(Q(pk__in=queryset) & Q(profile_reviewed=False))
    this_profile = None
    this_profile_description = None

    show_profile = request.method == 'POST' and 'my_ceramic' in request.POST
    review = request.method == 'POST' and 'review' in request.POST

    if show_profile:
        ceramic_id = int(request.POST['my_ceramic'])
        this_profile = CeramicContour.objects.filter(find_id=ceramic_id)
        this_profile_description = PotteryDescription.objects.filter(pk=ceramic_id)[0]

    if review:
        action, object = request.POST['review'].split(' ')
        ceramic_id = int(object)
        if action == 'delete':
            queryset = CeramicContour.objects.filter(find_id=ceramic_id)
            this_ceramic = PotteryDescription.objects.filter(pk=ceramic_id)[0]
            for item in queryset:
                item.delete()
            this_ceramic.distance_to_center = None
            this_ceramic.save()
            this_profile_description = None
            logger.info(f'radinio profilis ištrintas: reg. nr. {this_ceramic.find_registration_nr}, {this_ceramic.research_object}')
        elif action == 'confirm':
            this_ceramic = PotteryDescription.objects.get(pk=ceramic_id)
            this_ceramic.profile_reviewed = True
            this_ceramic.save()
            this_profile_description = None
            logger.info(f'patvirtinta profilio kokybė: reg. nr. {this_ceramic.find_registration_nr}, {this_ceramic.research_object}')

    context = {
        'my_ceramic': ceramic_vectors,
        'profile': this_profile,
        'profile_description': this_profile_description
    }
    return render(request, 'my_ceramic.html', context=context)


@csrf_protect
def vectorize_drawings(request, object_id):
    messages.clear()
    if request.method == 'POST':
        form = DrawingForm(request.POST, request.FILES)
        if form.is_valid():
            files = request.FILES.getlist('drawing')
            frame_width = int(request.POST['frame_width'])
            frame_height = int(request.POST['frame_height'])
            frame_color = request.POST['frame_color']
            ceramic_color = request.POST['ceramic_color']
            ceramic_orientation = request.POST['ceramic_orientation']

            vectorize_files(files,
                            frame_width,
                            frame_height,
                            object_id,
                            ceramic_color,
                            frame_color,
                            ceramic_orientation)
        form = DrawingForm()
    else:
        form = DrawingForm()
    return render(request, 'read_drawings.html', {'form': form, 'messages': messages})
