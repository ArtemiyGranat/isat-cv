from enum import Enum

import entities
import numpy as np
from PIL import Image
from skimage import color


class ColorModel(int, Enum):
    LAB = 0
    HSV = 1


def compute_mean_color(image: Image, color_model: ColorModel):
    np_image = np.array(image)

    mask = np_image[..., 3] > 0
    np_image = np_image[..., :3][mask].reshape(-1, 3) / 255.0

    if color_model == ColorModel.LAB:
        converted_image = color.rgb2lab(np_image)
    else:
        converted_image = color.rgb2hsv(np_image)

    mean_color = np.mean(converted_image, axis=0)
    return mean_color


def mean_color(image: entities.Image, color_model: ColorModel):
    if color_model == ColorModel.LAB:
        return [image.mean_l, image.mean_a, image.mean_b]
    else:
        return [image.mean_h, image.mean_s, image.mean_v]


def color_distance(color, other_color, color_model: ColorModel):
    if color_model == ColorModel.HSV:
        return np.sqrt(np.sum((color - other_color) ** 2))
    else:
        return color.deltaE_ciede2000(color, other_color)
