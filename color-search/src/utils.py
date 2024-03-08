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
    async with ctx.image_repo.get_many() as images:
        with Image.open(target_image_bytes) as target_image:
            target_color = compute_mean_color(target_image, color_model)
        differences = [
            (
                color_distance(
                    target_color, mean_color(image, color_model), color_model
                ),
                image.url,
            )
            for image in images
        ]

    differences.sort()
    return [url for _, url in differences[:amount]]
