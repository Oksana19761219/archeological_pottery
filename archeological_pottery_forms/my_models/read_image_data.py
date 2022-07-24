from PIL import Image
import numpy as np
import pandas as pd
import logging
from .messages import messages



logger = logging.getLogger(__name__)


def flip_image(image, ceramic_orientation):
    if ceramic_orientation == 'left':
        image = image.transpose(Image.FLIP_TOP_BOTTOM)
    elif ceramic_orientation == 'right':
        image = image.transpose(Image.FLIP_LEFT_RIGHT)
        image = image.transpose(Image.FLIP_TOP_BOTTOM)
    return image


def get_data_from_image(image):
    data = image.getdata()
    data_np = np.array(data)
    return data_np


def _select_color(r, g, b, color):
    colors = {'red' : (r > 200) & (r - g > 150) & (r - b > 150),
              'green' : (g > 200) & (g - r > 100) & (g - b > 100),
              'blue' : (b > 200) & (b - g > 150) & (b - r > 150),
              'black' : (r < 60) & (g < 60) & (b < 60),
              'white' : (r > 210) & (g > 210) & (b > 210)
              }
    return colors[color]


def find_pixels(image, selected_color):
    pixels = get_data_from_image(image)
    r, g, b = pixels[:,0], pixels[:, 1], pixels[:,2]
    color = _select_color(r, g, b, selected_color)
    pixel_place = np.where(color)
    return pixel_place


def _calculate_pixel_coords(pixel_index, image_width):
    x = pixel_index % image_width
    y = pixel_index // image_width
    return x, y



def _get_pixels_coords(image, pixels):
    calculate_coordinates_v = np.vectorize(_calculate_pixel_coords)
    image_width = image.size[0]
    x, y = calculate_coordinates_v(pixels, image_width)
    return x, y


def find_frame_corners_coords(image, pixels):
    x, y = _get_pixels_coords(image, pixels)
    coordinates = list(zip(x[0], y[0]))
    if len(coordinates) >= 4:
        x_avg, y_avg = np.average(x), np.average(y)
        top_left = [c for c in coordinates if c[0] < x_avg and c[1] < y_avg]
        top_right = [c for c in coordinates if c[0] > x_avg and c[1] < y_avg]
        bottom_left = [c for c in coordinates if c[0] < x_avg and c[1] > y_avg]
        bottom_right = [c for c in coordinates if c[0] > x_avg and c[1] > y_avg]
        frame_coords = [top_left[0], top_right[0], bottom_left[0], bottom_right[0]]
        return frame_coords
    message = f'netinkamai nubraižytas rėmas, nepakanka taškų: {coordinates}'
    messages.append(message)
    logger.exception(message)
    return None


def _calculate_transform_coeffs(new_coords, old_coords):
    """
    calculate coefficients for image perspective transformation
    based on 4 points coordinates
    https://stackoverflow.com/questions/14177744/how-does-perspective-transformation-work-in-pil
    """
    matrix = []
    for c1, c2 in zip(new_coords, old_coords):
        matrix.append([c1[0], c1[1], 1, 0, 0, 0, -c2[0]*c1[0], -c2[0]*c1[1]])
        matrix.append([0, 0, 0, c1[0], c1[1], 1, -c2[1]*c1[0], -c2[1]*c1[1]])

    A = np.matrix(matrix, dtype=float)
    B = np.array(old_coords).reshape(8)

    res = np.dot(np.linalg.inv(A.T * A) * A.T, B)
    coeffs = np.array(res).reshape(8)
    return coeffs


def _calculate_new_frame_coords(old_frame_coords):
    top_left, \
    top_right, \
    bottom_left, \
    bottom_right = old_frame_coords

    frame_length = top_right[0] - top_left[0]

    top_left_new = top_left
    top_right_new = top_right[0], top_left[1]
    bottom_left_new = top_left[0], top_left[1] + frame_length
    bottom_right_new = top_right_new[0], bottom_left_new[1]

    new_frame_coords = [top_left_new, top_right_new, bottom_left_new, bottom_right_new]
    return new_frame_coords


def _resize_image(image, frame_width_mm, frame_height_mm, frame_coords):

    frame_width_px = frame_coords[1][0] - frame_coords[0][0]
    frame_height_px = frame_coords[2][1] - frame_coords[0][1]

    image_width, image_height = image.size

    width_coeff = (frame_width_mm / frame_width_px)*5 # result: image dpi= 5px/mm
    height_coeff = (frame_height_mm / frame_height_px)*5 # result: image dpi= 5px/mm

    new_image_width = int(image_width * width_coeff)
    new_image_height = int(image_height * height_coeff)

    image = image.resize((new_image_width, new_image_height), Image.Resampling.LANCZOS)
    return image


def orthogonalize_image(image, pixels, frame_width, frame_height):
    old_frame_coords = find_frame_corners_coords(image, pixels)
    new_frame_coords = _calculate_new_frame_coords(old_frame_coords)
    coeffs = _calculate_transform_coeffs(new_frame_coords, old_frame_coords)
    width, height = image.size
    image = image.transform((width, height),
                            Image.Transform.PERSPECTIVE, coeffs,
                            Image.Resampling.BICUBIC)
    image = _resize_image(image, frame_width, frame_height, new_frame_coords)
    return image


def _scan_contour(coordinates, group_field, diff_field):
    coords_grouped = coordinates.groupby(group_field)
    coords_min = coords_grouped.min().reset_index()
    coords_max = coords_grouped.max().reset_index()

    inner_contour_indexes = list(coords_grouped.diff(periods=1)
                                [coords_grouped.diff(periods=1)[diff_field] > 1]
                                .index)
    inner_contour_indexes = inner_contour_indexes + [index-1 for index in inner_contour_indexes]
    inner_contour_coords = coordinates.iloc[inner_contour_indexes]

    coords_contour = pd.concat([coords_min, coords_max, inner_contour_coords])
    return coords_contour


def get_contour_coords(image, ceramic_pixels, frame_pixels, ceramic_id):
    x, y = _get_pixels_coords(image, ceramic_pixels)
    coords = pd.DataFrame({'x': x[0], 'y': y[0]})

    coords_scanned_x_axis = _scan_contour(coords, 'x', 'y')
    coords_snanned_y_axis = _scan_contour(coords, 'y', 'x')
    coords_all = pd.concat([coords_scanned_x_axis, coords_snanned_y_axis])\
                            .drop_duplicates()\
                            .sort_values(by=['x', 'y'])
    x_min = coords_all['x'].min()
    y_min = coords_all['y'].min()
    distance_to_pot_center = find_frame_corners_coords(image, frame_pixels)[0][0] - x_min

    coords_all['x'] = coords_all['x'].apply(lambda  x: x-x_min)
    coords_all['y'] = coords_all['y'].apply(lambda y: y - y_min)
    coords_all['find'] = ceramic_id
    return coords_all, distance_to_pot_center

