from django.db.models import Q
from ..models import PotteryDescription, CeramicContour
import logging
from PIL import Image
from .read_image_data import \
    flip_image, \
    find_pixels, \
    find_frame_corners_coords, \
    orthogonalize_image, \
    get_contour_coords
from .my_decorators import calculate_time
from .messages import messages


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
            message = f'nepatvirtintas radinio unikalumas CeramicContour modelyje (reg. nr. {str(file)}, objekto id {object_id})'
            messages.append(message)
            logger.exception(message)
    else:
        message = f'nepatvirtintas radinio unikalumas PotteryDescription modelyje (reg. nr. {str(file)}, objekto id {object_id})'
        messages.append(message)
        logger.exception(message)
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


def _write_coords_to_model(contour_coords, distance_to_pot_center, ceramic_id):
    if  distance_to_pot_center and not contour_coords.empty:
        this_ceramic = PotteryDescription.objects.get(pk=ceramic_id)
        this_ceramic.distance_to_center = distance_to_pot_center
        this_ceramic.save()
        _write_coordinates_to_model(contour_coords)
        message = f'įrašytos profilio koordinatės: reg. nr. {this_ceramic.find_registration_nr}, {this_ceramic.research_object}'
        messages.append(message)
        logger.info(message)
    else:
        this_ceramic = PotteryDescription.objects.get(pk=ceramic_id)
        message = f'nepavyko nuskaityti profilio koordinačių, reg. nr. {this_ceramic.find_registration_nr}, {this_ceramic.research_object}'
        messages.append(message)
        logger.exception(message)


def _vectorize_one_file(file,
                        ceramic_id,
                        ceramic_color,
                        frame_color,
                        frame_width,
                        frame_height,
                        ceramic_orientation):
    image = Image.open(file)
    flipped_image = flip_image(image, ceramic_orientation)

    frame_pixels = find_pixels(flipped_image, frame_color)
    ceramic_pixels = find_pixels(flipped_image, ceramic_color)
    frame_pixels_exist = len(frame_pixels[0]) > 0
    ceramic_pixels_exist = len(ceramic_pixels[0]) > 0

    if frame_pixels_exist and ceramic_pixels_exist:
        frame_corners_coords = find_frame_corners_coords(flipped_image, frame_pixels)
        if frame_corners_coords:
            ortho_image = orthogonalize_image(flipped_image,
                                              frame_pixels,
                                              frame_width,
                                              frame_height)
            ceramic_pixels = find_pixels(ortho_image, ceramic_color)
            frame_pixels = find_pixels(ortho_image, frame_color)
            ceramic_contour_coordinates, distance_to_pot_center = get_contour_coords(ortho_image,
                                                                                    ceramic_pixels,
                                                                                    frame_pixels,
                                                                                    ceramic_id)
            _write_coords_to_model(ceramic_contour_coordinates,
                                   distance_to_pot_center,
                                   ceramic_id)
        else:
            message = f'failas {file} nevektorizuotas, nes nepavyko nuskaityti rėmo kampų koordinačių'
            messages.append(message)
            logger.exception(message)
    else:
        message = f' brėžinyje nepavyko rasti pasirinktų spalvų: {file}, rėmo spalva {frame_color}, keramikos profilio spalva {ceramic_color}'
        messages.append(message)
        logger.exception(message)


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
            if ceramic_id:
                _vectorize_one_file(file,
                                    ceramic_id,
                                    ceramic_color,
                                    frame_color,
                                    frame_width,
                                    frame_height,
                                    ceramic_orientation)
            else:
                message = f'brėžinys nevektorizuotas: {file}, tyrimų objekto id {object_id}'
                messages.append(message)
                logger.exception(message)
    else:
        message = f'netinkamai įvesti duomenys: files: {files}, frame_width: {frame_width}, frame_height: {frame_height}'
        messages.append(message)
        logger.exception(message)
