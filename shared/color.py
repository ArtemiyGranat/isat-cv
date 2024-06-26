import numpy as np
from PIL import Image
from skimage import color

from shared.entities import Image as ImageEntity
from shared.models import ColorModel


def compute_mean_color(image: Image, color_model: ColorModel):
    np_image = np.array(image)

    mask = np_image[..., 3] > 0
    # TODO: normalized image is better name maybe?
    np_image = np_image[..., :3][mask].reshape(-1, 3) / 255.0

    if color_model == ColorModel.LAB:
        converted_image = color.rgb2lab(np_image)
    else:
        converted_image = color.rgb2hsv(np_image)

    mean_color = np.mean(converted_image, axis=0)
    return mean_color


def mean_color(image: ImageEntity, color_model: ColorModel):
    if color_model == ColorModel.LAB:
        return image.lab
    else:
        return image.hsv


def color_distance(target_color, other_color, color_model: ColorModel):
    if color_model == ColorModel.HSV:
        return np.sqrt(np.sum((target_color - other_color) ** 2))
    else:
        return color.deltaE_ciede2000(target_color, other_color)
