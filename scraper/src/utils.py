import logging
import os
from dataclasses import dataclass
from urllib.parse import urljoin

from bs4 import Tag
from context import ctx

logger = logging.getLogger("app")


@dataclass
class ScraperInfo:
    images_scraped: int


def process_image(image: Tag, info: ScraperInfo) -> int:
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
        info.images_scraped += 1
    else:
        logger.error(f"Failed to download image from {url}")
