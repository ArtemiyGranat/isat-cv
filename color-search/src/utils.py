from cs_context import ctx

from shared.color import ColorModel, color_distance, mean_color


def similar_color(target_image, color_model: ColorModel, amount: int = 10):
    # FIXME: mean_color() of target image
    target_color = [0.0, 0.0, 0.0]

    differences = []

    images = ctx.image_repo.get_many()
    for image in images:
        img_color = mean_color(image)
        diff = color_distance(target_color, img_color, color_model)
        differences.append((diff, image.url))

    differences.sort()

    return [url for _, url in differences[:amount]]
