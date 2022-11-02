from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, reverse, redirect
from django.contrib import messages
from django.contrib.auth.forms import User
from django.views.decorators.csrf import csrf_protect
from django.db.models import Q, Max, Count, Min, Avg, Func, F
from .models import Bibliography, \
                    PotteryDescription, \
                    ResearchObject, \
                    CeramicContour, \
                    ContourCorrelation,\
                    ContourGroup
from .forms import PotteryDescriptionForm, DrawingForm, ContourGroupForm
from .my_models.vectorize_files import vectorize_files
from .my_models.variables import messages, choosed_ids, ids_group
from .my_models.correlation import calculate_correlation
from .my_models.sounds import sound_files
from .my_models.draw_image import draw_group_image
import numpy as np
import pandas as pd
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
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

    """
    Skaiciuoja dvieju buitines keramikos vertikaliu profiliu y koordinaciu koreliacijos koeficienta.
    Profilio koordinaciu sistemos centras (x=0,y=0) yra puodo sukimosi asies ir virsutines plokstumos susikirtime.
    Siuo metu funkcija ivertina visas imanomas duomenu bazeje esanciu radiniu kombinacijas
    """

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
def auto_group_contours(request):
    if request.method == 'POST' and 'create' in request.POST:
        correlation_x = request.POST['correlation']
        queryset_by_correlation = ContourCorrelation.objects. \
            filter(correlation_x__gte=correlation_x). \
            distinct(). \
            values_list('find_1', 'find_2')
        queryset_ids = list(
            {item[0] for item in queryset_by_correlation}. \
                union({item[1] for item in queryset_by_correlation})
        )
        objects_to_group = PotteryDescription.objects.filter(
            Q(pk__in=queryset_ids) &
            ~Q(groups__correlation_x=correlation_x)
        ).distinct()
        loop_count = 0
        for object in objects_to_group:
            loop_count+=1
            print(loop_count)
            corelated_objects = ContourCorrelation.objects.filter(
                (Q(find_1=object.id) | Q(find_2=object.id)) &
                Q(correlation_x__gte=correlation_x)
            ).distinct().\
            values_list('find_1', 'find_2')
            correlated_ids = list(
                {item[0] for item in corelated_objects if item != object.id}. \
                    union({item[1] for item in corelated_objects if item != object.id})
            )
            group_exist = PotteryDescription.objects.\
                filter(Q(pk__in=correlated_ids) & Q(groups__correlation_x=correlation_x)).\
                first()
            if not group_exist:
                group = ContourGroup(correlation_x=correlation_x, )
                group.save()
            else:
                group = group_exist. \
                    groups.all(). \
                    get(correlation_x=correlation_x). \
                    id
            object.groups.add(group)
            object.save()
        print(f'pabaiga, {loop_count}')

    return render(request, 'group_contours_auto.html')


def review_groups(request):
    contours = None
    this_group = None
    groups = ContourGroup.objects.\
        annotate(findings_count=Count('potterydescription__id')).\
        order_by('-correlation_x', '-findings_count').\
        filter(findings_count__gt=1)


    if request.method == 'POST' and 'groups' in request.POST:
        group = int(request.POST['groups'])

        y_max = CeramicContour.objects.aggregate(Max('y'))
        filter_solution = [item for item in range(0, y_max['y__max'], 1)] # laikinas kintamasis, reikalingas braizymo kokybei sumazinti, pagreitinti atvaizdavima

        contours = CeramicContour.objects.filter(Q(find_id__groups=group) & Q(y__in=filter_solution)).distinct('x', 'y')
        this_group = group

    if request.method == 'POST' and 'draw_image' in request.POST:
        group_id = int(request.POST['draw_image'])
        group = ContourGroup.objects.\
            annotate(findings_count=Count('potterydescription__id')).\
            get(pk=group_id)

        x_min = CeramicContour.objects.filter(y=0).\
            values('y', 'find_id').\
            annotate(x_min=Avg('x')).\
            order_by().\
            values_list('find_id', 'x_min')

        coords = CeramicContour.objects.\
            filter(find_id__groups=group.id).\
            values_list('find_id', 'x', 'y')

        draw_group_image(group, coords, x_min)


    if request.method == 'POST' and 'draw_images' in request.POST:
        group_id = int(request.POST['draw_images'])
        group_correlation = ContourGroup.objects.get(pk=group_id).correlation_x
        groups = ContourGroup.objects.filter(correlation_x=group_correlation).values_list('id')
        x_min = CeramicContour.objects.filter(y=0).\
            values('y', 'find_id').\
            annotate(x_min=Avg('x')).\
            order_by().\
            values_list('find_id', 'x_min')

        for group in groups:
            group_id = group[0]
            group = ContourGroup.objects. \
                annotate(findings_count=Count('potterydescription__id')). \
                get(pk=group_id)

            coords = CeramicContour.objects. \
                filter(find_id__groups=group.id). \
                values_list('find_id', 'x', 'y')

            draw_group_image(group, coords, x_min)
        # print('atlikta')


    context = {
        'groups': groups,
        'contours': contours,
        'this_group': this_group
    }
    return render(request, 'review_groups.html', context=context)

