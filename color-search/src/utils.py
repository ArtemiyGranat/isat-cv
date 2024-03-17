from cs_context import ctx
from PIL import Image

from shared.color import (
    color_distance,
    compute_mean_color,
    mean_color,
)
from shared.models import ColorModel


async def similar_color(
    target_image_as_bytes, color_model: ColorModel, amount: int = 10
):
    with Image.open(target_image_as_bytes) as target_image:
        target_color = compute_mean_color(target_image, color_model)

    differences = []
    for image in await ctx.image_repo.get_many():
        color = mean_color(image, color_model)
        distance = color_distance(target_color, color, color_model)
        differences.append((distance, image.url))

    differences.sort()

    return [url for _, url in differences[:amount]]
