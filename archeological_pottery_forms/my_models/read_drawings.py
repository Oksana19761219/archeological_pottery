from PIL import Image
import numpy as np
import pandas as pd


def get_data_from_image(im):
    data = im.getdata()
    data_np = np.array(data)
    return data_np


def select_color(r, g, b, color):
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
    color = select_color(r, g, b, selected_color)
    pixel_place = np.where(color)
    return pixel_place

def calculate_pixel_coords(pixel_index, image_width):
    x = pixel_index % image_width
    y = pixel_index // image_width
    return x, y


def get_pixels_coords(image, selected_color):
    pixel_place = find_pixels(image, selected_color)
    calculate_coordinates_v = np.vectorize(calculate_pixel_coords)
    image_width = image.size[0]
    x, y = calculate_coordinates_v(pixel_place, image_width)
    return x, y


def find_frame_corners_coords(image, selected_color):
    x, y = get_pixels_coords(image, selected_color)
    coordinates = list(zip(x[0], y[0]))
    x_avg, y_avg = np.average(x), np.average(y)
    top_left = [c for c in coordinates if c[0] < x_avg and c[1] < y_avg]
    top_right = [c for c in coordinates if c[0] > x_avg and c[1] < y_avg]
    bottom_left = [c for c in coordinates if c[0] < x_avg and c[1] > y_avg]
    bottom_right = [c for c in coordinates if c[0] > x_avg and c[1] > y_avg]
    frame_coords = [top_left[0], top_right[0], bottom_left[0], bottom_right[0]]
    return frame_coords


def calculate_transform_coeffs(new_coords, old_coords):
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


def calculate_new_frame_coords(old_frame_coords):
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


def resize_image(image, frame_width_mm, frame_height_mm, frame_coords):

    frame_width_px = frame_coords[1][0] - frame_coords[0][0]
    frame_height_px = frame_coords[2][1] - frame_coords[0][1]

    image_width, image_height = image.size

    width_coeff = frame_width_mm / frame_width_px
    height_coeff = frame_height_mm / frame_height_px

    new_image_width = int(image_width * width_coeff)
    new_image_height = int(image_height * height_coeff)

    image = image.resize((new_image_width, new_image_height), Image.Resampling.LANCZOS)
    return image


def transform_image(image, selected_color, frame_width, frame_height):
    old_frame_coords = find_frame_corners_coords(image, selected_color)
    new_frame_coords = calculate_new_frame_coords(old_frame_coords)
    coeffs = calculate_transform_coeffs(new_frame_coords, old_frame_coords)
    width, height = image.size
    image = image.transform((width, height),
                            Image.Transform.PERSPECTIVE, coeffs,
                            Image.Resampling.BICUBIC)
    image = resize_image(image, frame_width, frame_height, new_frame_coords)
    return image


def get_contour_coords(image, selected_color):
    x, y = get_pixels_coords(image, selected_color)
    coords_all = pd.DataFrame({'x': x[0], 'y': y[0]})
    coords_grouped = coords_all.groupby('y')
    coords_min = coords_grouped.min().reset_index()
    coords_max = coords_grouped.max().reset_index()

    indexes_intermediate = list(coords_grouped.diff(periods=1)
                                [coords_grouped.diff(periods=1)['x'] > 1]
                                .index)
    coords_intermediate = coords_all.iloc[indexes_intermediate]

    coords_contour = pd.concat([coords_min, coords_max, coords_intermediate])
    return coords_contour

