from django.db.models import Q
from ..models import PotteryDescription, CeramicContour
import logging
from .read_image_data import read_image_data
from .my_decorators import calculate_time


logger = logging.getLogger(__name__)


def _get_ceramic_id(file, object_id):
    find_id = []
    file_name = str(file).split('.')[0]
    queryset = PotteryDescription.objects.filter(
        Q(find_registration_nr__exact=file_name) &
        Q(research_object__exact=object_id)
    )
    for item in queryset:
        find_id.append(item.id)
    if len(find_id) == 1:
        unique_profile = not CeramicContour.objects.filter(find_id=find_id[0])
        if unique_profile:
            return find_id[0]
        else:
            logger.info(f'nepatvirtintas radinio unikalumas CeramicContour modelyje (reg. nr. {str(file)}, objekto id {object_id})')
    else:
        logger.info(f'nepatvirtintas radinio unikalumas PotteryDescription modelyje (reg. nr. {str(file)}, objekto id {object_id})')
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


def _vectorize_one_file(file,
                        ceramic_id,
                        ceramic_color,
                        frame_color,
                        frame_width,
                        frame_height,
                        ceramic_orientation):
    if ceramic_id:
        contour_coords, distance_to_pot_center = read_image_data(file,
                                                                ceramic_id,
                                                                ceramic_color,
                                                                frame_color,
                                                                frame_width,
                                                                frame_height,
                                                                ceramic_orientation)
        if not contour_coords.empty and distance_to_pot_center:
            this_ceramic = PotteryDescription.objects.get(pk=ceramic_id)
            this_ceramic.distance_to_center = distance_to_pot_center
            this_ceramic.save()
            _write_coordinates_to_model(contour_coords)
            logger.info(f'įrašytos profilio koordinatės: reg. nr. {this_ceramic.find_registration_nr}, {this_ceramic.research_object}')


@calculate_time
def vectorize_files(files,
                    frame_width,
                    frame_height,
                    object_id,
                    ceramic_color,
                    frame_color,
                    ceramic_orientation):

    if files and frame_width > 0 and frame_height > 0:
        for file in files:
            ceramic_id = _get_ceramic_id(file, object_id)
            _vectorize_one_file(file,
                                ceramic_id,
                                ceramic_color,
                                frame_color,
                                frame_width,
                                frame_height,
                                ceramic_orientation)
    else:
        logger.info(f'įvesti duomenys neatitinka sąlygos: files: {files}, frame_width: {frame_width}, frame_height: {frame_height}')
