import logging
import os
from urllib.parse import urljoin

from bs4 import Tag
from context import ctx

logger = logging.getLogger("app")


def process_image(image: Tag) -> int:
    url = urljoin(ctx.config.start_url, image["src"])
    img_name = os.path.join(ctx.config.img_dir, os.path.basename(url))

    if os.path.splitext(img_name)[-1] == "":
        img_name = img_name + ".jpg"

    if os.path.exists(img_name):
        logger.info(f"{url} already exists")
        return

    image_response = ctx.http_client.get(url)

    if image_response.status_code == 200:
        with open(img_name, "wb") as f:
            f.write(image_response.content)
    else:
        logger.error(f"Failed to download image from {url}")

    return image_response.status_code
