from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, reverse, redirect
from django.contrib import messages
from django.contrib.auth.forms import User
from django.views.decorators.csrf import csrf_protect
from django.db.models import Q, Max, Avg, F
from .models import Bibliography, \
                    PotteryDescription, \
                    ResearchObject, \
                    CeramicContour, \
                    ContourCorrelation
from .forms import PotteryDescriptionForm, DrawingForm
from .my_models.vectorize_files import vectorize_files
from .my_models.variables import messages, choosed_ids, ids_group
from .my_models.correlation import calculate_correlation
from .my_models.sounds import sound_files
import pandas as pd
from math import pi
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
    this_object_vectors_count = this_object_vectors.count()

    context = {
        'object': single_object,
        'reports': reports,
        'vectors': this_object_vectors,
        'vectors_count': this_object_vectors_count
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
            sound_files()
        form = DrawingForm()
    else:
        form = DrawingForm()
    return render(request, 'read_drawings.html', {'form': form, 'messages': messages})


def get_queryset_type(request):
    if 'queryset_type' in request.POST:
        return request.POST['queryset_type']
    else:
        return 'contour'


def get_correlated_contours(contour_1_id, corr_min, corr_max, queryset_type):
    if queryset_type == 'contour':
        queryset = PotteryDescription.objects.all()
    elif queryset_type == 'contour_lip':
        lip_id = PotteryDescription.objects.get(pk=contour_1_id).lip_id
        queryset = PotteryDescription.objects.filter(lip_id=lip_id)
    elif queryset_type == 'contour_ornament':
        ornament_id = PotteryDescription.objects.get(pk=contour_1_id).ornament_id
        queryset = PotteryDescription.objects.filter(ornament_id=ornament_id)
    elif queryset_type == 'contour_ornament_lip':
        object = PotteryDescription.objects.get(pk=contour_1_id)
        lip_id, ornament_id = object.lip_id, object.ornament_id
        queryset = PotteryDescription.objects.filter(Q(lip_id=lip_id) & Q(ornament_id=ornament_id))
    id_list = list(queryset.values_list('pk', flat=True))
    contours_queryset = ContourCorrelation.objects.filter(Q(find_1__in=id_list) & Q(find_2__in=id_list))
    return contours_queryset.filter(
            (Q(find_1=contour_1_id) | Q(find_2=contour_1_id)) &
            (Q(correlation_x__gte=corr_min) & Q(correlation_x__lte=corr_max))
        ).order_by('-correlation_x', '-length_compared')


@csrf_protect
def view_correlation(request):
    my_ceramic = PotteryDescription.objects.filter(coordinates__isnull=False).distinct()
    object_1, object_2 = None, None
    contour_1, contour_2  = None, None
    correlated_contours = None
    contour_1_id = None
    corr_min, corr_max = None, None
    corr_coeff = None
    queryset_type = 'contour'

    select_1_contour = request.method == 'POST' and 'my_ceramic' in request.POST
    select_2_contour = request.method == 'POST' and 'correlated_contours' in request.POST

    if select_1_contour:
        contour_1_id = int(request.POST['my_ceramic'])
        contour_1 = CeramicContour.objects.filter(Q(find__profile_reviewed=True) & Q(find_id=contour_1_id))
        object_1 = my_ceramic.filter(pk=contour_1_id)

        correlation = float(request.POST['correlation1']), float(request.POST['correlation2'])
        corr_min = min(correlation)
        corr_max= max(correlation)

        queryset_type = get_queryset_type(request)
        correlated_contours = get_correlated_contours(contour_1_id, corr_min, corr_max, queryset_type)

    if select_2_contour:
        data = request.POST['correlated_contours'].split()
        contour_1_id = data[0]
        corr_min, corr_max = data[1], data[2]
        corr_coeff = data[3]
        queryset_type = data[4]
        ids = data[5:]
        ids.remove(contour_1_id)
        contour_2_id = int(ids[0])

        contour_1 = CeramicContour.objects.filter(find_id=contour_1_id)
        contour_2 = CeramicContour.objects.filter(find_id=contour_2_id)
        object_1 = my_ceramic.filter(pk=contour_1_id)
        object_2 = my_ceramic.filter(pk=contour_2_id)
        correlated_contours = get_correlated_contours(contour_1_id, corr_min, corr_max, queryset_type)

    context = {
        'my_ceramic': my_ceramic,
        'contour_1_id': contour_1_id,
        'contour_1': contour_1,
        'contour_2': contour_2,
        'correlated_contours': correlated_contours,
        'corr_min': corr_min,
        'corr_max': corr_max,
        'object_1': object_1,
        'object_2': object_2,
        'corr_coeff': corr_coeff,
        'queryset_type': queryset_type
    }
    return render(request, 'view_correlation.html', context=context)

import time


@csrf_protect
def calculate_correlation_coefficient(request):
    correlated_ids = PotteryDescription.objects.\
        filter(correlation_calculated=True).\
        distinct().\
        values_list('pk', flat=True)
    ids_to_correlate = PotteryDescription.objects.\
        filter(Q(correlation_calculated=False) & Q(profile_reviewed=True)).\
        distinct().\
        values_list('pk', flat=True)
    contours_correlated = CeramicContour.objects.filter(find_id__in=correlated_ids).values()
    contours_to_correlate = CeramicContour.objects.filter(find_id__in=ids_to_correlate).values()
    contours_correlated_df = pd.DataFrame.from_records(contours_correlated)
    contours_to_correlate_df = pd.DataFrame.from_records(contours_to_correlate)

    if not contours_correlated_df.empty:
        contours_correlated_quantity = len(contours_correlated_df['find_id'].unique())
    else:
        contours_correlated_quantity = 0

    if not contours_to_correlate_df.empty:
        contours_to_correlate_quantity = len(contours_to_correlate_df['find_id'].unique())
    else:
        contours_to_correlate_quantity = 0

    if request.method == 'POST' and not contours_to_correlate_df.empty:
        start_time = time.perf_counter()
        ids = contours_to_correlate_df['find_id'].unique()

        for id in sorted(ids):
            this_contour = contours_to_correlate_df[contours_to_correlate_df['find_id'] == id]
            other_contours = contours_to_correlate_df[contours_to_correlate_df['find_id'] > id]

            if not other_contours.empty:
                calculate_correlation(this_contour, other_contours, id)

            if not contours_correlated_df.empty:
                calculate_correlation(this_contour, contours_correlated_df, id)
        this_ceramic = PotteryDescription.objects.get(pk=id)
        this_ceramic.correlation_calculated = True
        this_ceramic.save()

        sound_files()
        end_time = time.perf_counter()
        run_time = end_time - start_time
        logger.info(f'koreliacijos koeficientai skaičiuoti {run_time} sek., lyginta {contours_correlated_quantity + contours_to_correlate_quantity} radinių')

    context = {
       'contours_correlated_quantity': contours_correlated_quantity,
        'contours_to_correlate_quantity': contours_to_correlate_quantity
    }
    return render(request, 'calculate_correlation.html', context=context)


@csrf_protect
def review_profiles(request):
    ids = CeramicContour.objects.values_list('find_id').distinct()
    objects = PotteryDescription.objects.filter(Q(profile_reviewed=False) & Q(pk__in=ids))
    object = objects.first()
    objects_to_review_quantity = objects.count()
    if object:
        this_profile = CeramicContour.objects.filter(find_id=object.id)
    else:
        this_profile = None

    if request.method == 'POST':
        action = request.POST['review']

        if object and action == 'delete':
            data_to_delete = CeramicContour.objects.filter(find_id=object.id)
            for item in data_to_delete:
                item.delete()
            object.distance_to_center = None
            logger.info(f'radinio profilis ištrintas: reg. nr. {object.find_registration_nr}, {object.research_object}')

        elif object and action == 'confirm':
            object.profile_reviewed = True
            object.save()
            logger.info(f'patvirtinta profilio kokybė, paskaičiuotas koreliacijos koeficientas: reg. nr. {object.find_registration_nr}, {object.research_object}')

    context = {
        'object': object,
        'this_profile': this_profile,
        'objects_to_review_quantity': objects_to_review_quantity
    }

    return render(request, 'review_profiles.html', context=context)


# def calculate_angle():
#     queryset = PotteryDescription.objects.filter(Q(coordinates__isnull=False) & Q(arc_angle=None)).distinct()
#     ids = queryset.values_list('id')
#
#     for id in ids:
#         x_max = CeramicContour.objects.filter(Q(find_id__in=id) & Q(y=0)).aggregate(Max('x'))['x__max']
#         arc_length = PotteryDescription.objects.filter(pk__in=id).values('arc_length')[0]['arc_length']
#         distance_to_center = PotteryDescription.objects.filter(pk__in=id).values('distance_to_center')[0]['distance_to_center']
#         radius = x_max + abs(distance_to_center)
#         angle = round((360 * (arc_length * 5))/(2 * pi * radius), 0)
#
#         object = PotteryDescription.objects.get(pk=id[0])
#         object.arc_angle = angle
#         object.save()

def calculate_length():
    queryset = PotteryDescription.objects.filter(Q(coordinates__isnull=False) & Q(find_length=None)).distinct()
    ids = queryset.values_list('id')
    for id in ids:
        length = CeramicContour.objects.filter(find_id=id).aggregate(Max('y'))['y__max']
        object = PotteryDescription.objects.get(pk=id[0])
        object.find_length = length
        object.save()


@csrf_protect
def choose_contour(request):
    objects = PotteryDescription.objects.\
        filter(Q(coordinates__isnull=False) & Q(contour_group=None)).\
        distinct().\
        order_by('-find_length', '-arc_angle')
    this_contour = None
    this_object = None

    show_contour = 'submit_show' in request.POST and 'my_ceramic' in request.POST
    choose_this_contour = 'submit_choose' in request.POST

    if request.method == 'POST' and show_contour:
        id = int(request.POST['my_ceramic'])
        this_contour = CeramicContour.objects.filter(find_id=id)
        this_object = PotteryDescription.objects.get(pk=id)

    if request.method == 'POST' and choose_this_contour:
        object_id = int(request.POST['submit_choose'])
        return HttpResponseRedirect(reverse('group_contours', args=[object_id]))

    context = {
        'objects': objects,
        'this_object': this_object,
        'this_contour': this_contour,
    }
    return render(request, 'choose_contour.html', context=context)


def group_contours(request, object_id):
    this_contour = CeramicContour.objects.filter(find_id=object_id)
    correlated_contours = ContourCorrelation.objects.\
        filter(
        (Q(find_1=object_id) | Q(find_2=object_id)) &
        Q(correlation_x__gte=0.95)). \
        order_by('-correlation_x', '-correlation_width', '-length_compared').\
        distinct()
    other_contour = None
    other_contour_id = None

    # correlated_ids = {item[0] for item in correlated_contours.values_list('find_1', 'find_2') if item[0] != object_id}.\
    #     union({item[1] for item in correlated_contours.values_list('find_1', 'find_2') if item[1] != object_id})
    # correlated_ids = list(correlated_ids)
    # correlated_objects = PotteryDescription.objects.filter(pk__in=correlated_ids)
    # print(len(correlated_ids))

    if request.method == 'POST' and 'my_ceramic' in request.POST:
        ids = request.POST['my_ceramic']
        other_contour_id = int(ids.replace(str(object_id), '').strip())
        other_contour = CeramicContour.objects.filter(find_id=other_contour_id)

    if request.method == 'POST' and 'submit_group' in request.POST:
        group_id = int(request.POST['submit_group'])
        ids_group['group_ids'].append(group_id)
        correlated_contours = correlated_contours. \
            exclude(Q(find_1__in=choosed_ids) | Q(find_2__in=choosed_ids))
        print(ids_group)
    if request.method == 'POST' and 'submit_nogroup' in request.POST:
        nogroup_id = int(request.POST['submit_nogroup'])
        ids_group['nogroup_ids'].append(nogroup_id)
        correlated_contours = correlated_contours. \
            exclude(Q(find_1__in=choosed_ids) | Q(find_2__in=choosed_ids))
        print(ids_group)

    context = {
        'this_contour': this_contour,
        'correlated_contours': correlated_contours,
        'other_contour': other_contour,
        'other_contour_id': other_contour_id
    }
    return render(request, 'group_contours.html', context=context)