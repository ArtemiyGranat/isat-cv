from enum import Enum

import numpy as np
from PIL import Image
from skimage import color


class ColorModel(int, Enum):
    LAB = 0
    HSV = 1


def mean_color(image_path, color_model):
    image = Image.open(image_path).convert("RGBA")
    np_image = np.array(image)

    mask = np_image[..., 3] > 0
    np_image = np_image[..., :3][mask].reshape(-1, 3) / 255.0

    if color_model == ColorModel.LAB:
        converted_image = color.rgb2lab(np_image)
    else:
        converted_image = color.rgb2hsv(np_image)

    mean_color = np.mean(converted_image, axis=0)
    return mean_color
