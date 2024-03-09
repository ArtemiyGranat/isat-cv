from cs_context import ctx
from PIL import Image

from shared.color import (
    ColorModel,
    color_distance,
    compute_mean_color,
    mean_color,
)


async def similar_color(
    target_image_bytes, color_model: ColorModel, amount: int = 10
):
    with Image.open(target_image_bytes) as target_image:
        target_color = compute_mean_color(target_image, color_model)

    differences = []

    images = await ctx.image_repo.get_many()
    for image in images:
        img_color = mean_color(image, color_model)
        diff = color_distance(target_color, img_color, color_model)
        differences.append((diff, image.url))

    differences.sort()

    return [url for _, url in differences[:amount]]
