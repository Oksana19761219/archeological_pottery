from django.db.models import Q
from ..models import PotteryDescription, CeramicContour
import logging
import pandas as pd
import  numpy as np
from PIL import Image
from .read_image_data import \
    flip_image, \
    find_pixels, \
    find_frame_corners_coords, \
    orthogonalize_image, \
    get_contour_coords
from .my_decorators import calculate_time
from .variables import messages
from .sounds import  sound_one_file


logger = logging.getLogger(__name__)


def _find_closest_node(node, nodes):
    dist = np.sum((nodes - node) ** 2, axis=1)
    closest_node = nodes[np.argmin(dist)]
    nodes = np.delete(nodes, np.argmin(dist), 0)
    return closest_node, nodes


def _calculate_curvature(ordered_nodes):
    """
    calculate curve curvature:
    https://stackoverflow.com/questions/28269379/curve-curvature-in-numpy
    """
    dx_dt = np.gradient(ordered_nodes[:, 0])
    dy_dt = np.gradient(ordered_nodes[:, 1])
    d2x_dt2 = np.gradient(dx_dt)
    d2y_dt2 = np.gradient(dy_dt)
    curvature = (d2x_dt2 * dy_dt - dx_dt * d2y_dt2) / (dx_dt * dx_dt + dy_dt * dy_dt) ** 1.5
    return curvature


def _order_curve_nodes(nodes):
    start_node = nodes.iloc[0]
    nodes = nodes.drop(index=0)
    nodes = np.asarray(nodes)
    node = np.asarray(start_node)
    ordered_nodes = node
    for item in range(len(nodes)):
        node, nodes = _find_closest_node(node, nodes)
        ordered_nodes = np.vstack([ordered_nodes, node])
    return ordered_nodes


def _split_profile(nodes):
    """
    :param nodes: ceramic profile coordinates x, y
    :return: outer and inner contours of ceramic profile
    """
    grouped_nodes = nodes.groupby(['y'])
    min_x = grouped_nodes['x'].min().reset_index()
    inner_contour = pd.merge(nodes, min_x, how='inner', on=['x', 'y'])
    min_x['min'] = True
    outer_contour = pd.merge(nodes, min_x, how='left', on=['x', 'y'])
    outer_contour = outer_contour[outer_contour['min'] != True]
    outer_contour = outer_contour.drop(['min'], axis=1)
    inner_contour = inner_contour.sort_values(by=['y', 'x']).reset_index().drop(['index'], axis=1)
    outer_contour = outer_contour.sort_values(by=['y', 'x']).reset_index().drop(['index'], axis=1)
    return inner_contour, outer_contour


def _clear_profile_line(nodes):
    nodes = nodes.sort_values(['y', 'x'])
    differences = nodes.diff()
    index_to_drop = differences[differences['x'] == 1].index
    nodes = nodes.drop(index_to_drop, axis=0)
    return nodes


def _create_ceramiccontour_records(nodes):
    nodes = _clear_profile_line(nodes)
    inner_contour, outer_contour = _split_profile(nodes)
    ordered_nodes_inner = _order_curve_nodes(inner_contour)
    ordered_nodes_outer = _order_curve_nodes(outer_contour)
    curvature_inner = _calculate_curvature(ordered_nodes_inner)
    curvature_outer = _calculate_curvature(ordered_nodes_outer)

    nodes_curvature_inner = np.c_[ordered_nodes_inner, curvature_inner]
    nodes_curvature_outer = np.c_[ordered_nodes_outer, curvature_outer]

    nodes_inner_pd = pd.DataFrame(data=nodes_curvature_inner, columns=['x', 'y', 'curvature'])
    nodes_inner_pd['profile_side'] = 'inner'

    nodes_outer_pd = pd.DataFrame(data=nodes_curvature_outer, columns=['x', 'y', 'curvature'])
    nodes_outer_pd['profile_side'] = 'outer'
    nodes_pd = pd.concat([nodes_inner_pd, nodes_outer_pd])
    return nodes_pd


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
            message = f'toks radinys jau yra CeramicContour modelyje (reg. nr. {str(file)}, objekto id {object_id})'
            messages.append(message)
            logger.exception(message)
    else:
        message = f'toks radinys jau yra PotteryDescription modelyje (reg. nr. {str(file)}, objekto id {object_id})'
        messages.append(message)
        logger.exception(message)
        return None




# def _write_dataframe_coords(coordinates):
#     """How to write a Pandas Dataframe to Django model
#     https://newbedev.com/how-to-write-a-pandas-dataframe-to-django-model"""
#     if not coordinates.empty:
#         df_records = coordinates.to_dict('records')
#         model_instances = [CeramicContour(
#             x=record['x'],
#             y=record['y'],
#             find_id=record['find']
#         ) for record in df_records]
#         CeramicContour.objects.bulk_create(model_instances)



def _write_records_to_model(nodes_records, ceramic_id):
    """How to write a Pandas Dataframe to Django model
    https://newbedev.com/how-to-write-a-pandas-dataframe-to-django-model"""

    if  not nodes_records.empty:
        records_dict = nodes_records.to_dict('records')
        model_instances = [CeramicContour(
            x=int(record['x']),
            y=int(record['y']),
            curvature=record['curvature'],
            profile_side=record['profile_side'],
            find_id=ceramic_id
        ) for record in records_dict]
        CeramicContour.objects.bulk_create(model_instances)
        message = f'įrašytos profilio koordinatės: id {ceramic_id}'
        messages.append(message)
        logger.info(message)
    else:
        message = f'nepavyko nuskaityti profilio koordinačių, id {ceramic_id}'
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
            ceramic_contour_coordinates = get_contour_coords(ortho_image,
                                                            ceramic_pixels,
                                                            frame_pixels,
                                                            ceramic_id)
            nodes = ceramic_contour_coordinates[['x', 'y']]
            nodes_records = _create_ceramiccontour_records(nodes)
            _write_records_to_model(nodes_records, ceramic_id)

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
                sound_one_file()
            else:
                message = f'brėžinys nevektorizuotas: {file}, tyrimų objekto id {object_id}'
                messages.append(message)
                logger.exception(message)
    else:
        message = f'netinkamai įvesti duomenys: files: {files}, frame_width: {frame_width}, frame_height: {frame_height}'
        messages.append(message)
        logger.exception(message)
