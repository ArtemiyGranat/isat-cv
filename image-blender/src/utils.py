from tempfile import SpooledTemporaryFile

import cv2
import numpy as np
from PIL import Image

# TODO: Refactor? This file looks huge and untidy


def process_images(first, second):
    images = [Image.open(img) for img in [first, second]]

    return [np.array(img)[:, :, [2, 1, 0]] for img in images]


def generate_gaussian_pyramid(img, levels):
    gaussian_pyramid = [img]
    for _ in range(levels):
        img = cv2.pyrDown(img)
        gaussian_pyramid.append(img)
    return gaussian_pyramid


def generate_laplacian_pyramid(gaussian_pyramid):
    laplacian_pyramid = [gaussian_pyramid[-1]]
    for i in range(len(gaussian_pyramid) - 1, 0, -1):
        size = (
            gaussian_pyramid[i - 1].shape[1],
            gaussian_pyramid[i - 1].shape[0],
        )
        laplacian_higher_level = cv2.pyrUp(gaussian_pyramid[i], dstsize=size)
        laplacian = cv2.subtract(
            gaussian_pyramid[i - 1], laplacian_higher_level
        )
        laplacian_pyramid.append(laplacian)
    return laplacian_pyramid


def blend_pyramids(pyramids):
    blended_pyramid = []
    for lap1, lap2 in pyramids:
        cols = lap1.shape[1]
        laplacian_blended = np.hstack(
            (lap1[:, 0 : int(cols / 2)], lap2[:, int(cols / 2) :])
        )
        blended_pyramid.append(laplacian_blended)

    return blended_pyramid


def reconstruct_from_pyramid(laplacian_pyramid):
    reconstructed_image = laplacian_pyramid[0]
    for i in range(1, len(laplacian_pyramid)):
        size = (laplacian_pyramid[i].shape[1], laplacian_pyramid[i].shape[0])
        reconstructed_image = cv2.pyrUp(reconstructed_image, dstsize=size)
        reconstructed_image = cv2.add(
            reconstructed_image, laplacian_pyramid[i]
        )

    return reconstructed_image


def blend_images(
    first_file: SpooledTemporaryFile, second_file: SpooledTemporaryFile
):
    imgs = process_images(first_file, second_file)

    imgs[1] = cv2.resize(
        imgs[1],
        (imgs[0].shape[1], imgs[0].shape[0]),
        interpolation=cv2.INTER_LINEAR,
    )

    # TODO: Add to context and config
    pyramids_levels = 3

    gaussian_pyramids = [
        generate_gaussian_pyramid(img, pyramids_levels) for img in imgs
    ]
    laplacian_pyramids = [
        generate_laplacian_pyramid(pyr) for pyr in gaussian_pyramids
    ]
    blended_pyramid = blend_pyramids(laplacian_pyramids)
    blended_image = reconstruct_from_pyramid(blended_pyramid)

    return Image.fromarray(blended_image)
