from tempfile import SpooledTemporaryFile

import cv2
import numpy as np
from PIL import Image


def process_images(first, second):
    images = [Image.open(img) for img in [first, second]]
    np_imgs = [np.array(img) for img in images]

    return [img[:, :, [2, 1, 0]] for img in np_imgs]


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


def blend_pyramids(lap_pyramid1, lap_pyramid2):
    blended_pyramid = []
    for lap1, lap2 in zip(lap_pyramid1, lap_pyramid2):
        rows, cols, dpt = lap1.shape
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

    gaussian_pyramid1 = generate_gaussian_pyramid(imgs[0], pyramids_levels)
    gaussian_pyramid2 = generate_gaussian_pyramid(imgs[1], pyramids_levels)
    laplacian_pyramid1 = generate_laplacian_pyramid(gaussian_pyramid1)
    laplacian_pyramid2 = generate_laplacian_pyramid(gaussian_pyramid2)

    blended_pyramid = blend_pyramids(laplacian_pyramid1, laplacian_pyramid2)

    blended_image = reconstruct_from_pyramid(blended_pyramid)

    # TODO: return to backend and visualize result
    cv2.imwrite("blended_image.jpg", blended_image)
