import io
import logging
import time
from uuid import uuid4

from bs4 import BeautifulSoup, Tag
from context import ctx
from httpx import Response
from imagehash import phash
from PIL import Image
from pydantic import BaseModel
from tenacity import retry, stop_after_attempt, wait_exponential

import shared.entities as entities

logger = logging.getLogger("app")


class ScraperInfo(BaseModel):
    images_scraped: int


@retry(stop=stop_after_attempt(7), wait=wait_exponential(multiplier=1, max=60))
async def get_with_retry(url: str) -> Response:
    response = await ctx.http_client.get(url)
    time.sleep(0.25)
    return response


def get_image_size_kb(image: Image.Image) -> float:
    buffer = io.BytesIO()
    image.save(buffer, ctx.config.img_save_extension)

    return buffer.tell() / 1024


def resize_image(img: Image.Image, init_size: float) -> Image.Image:
    compression_ratio = ctx.config.max_image_size_kb / init_size
    img = img.resize(
        (
            int(img.width * compression_ratio),
            int(img.height * compression_ratio),
        ),
        Image.LANCZOS,
    )

    return img


async def process_image(image: Tag, info: ScraperInfo) -> None:
    img_url = image["src"]
    if await ctx.image_repo.get_one(field="url", value=img_url) is not None:
        logger.info(f"{img_url} already exists")
        return

    response = await get_with_retry(img_url)
    if response.status_code != 200:
        logger.error(f"Failed to download image from {img_url}")
        return

    with Image.open(io.BytesIO(response.content)) as img:
        img_size_kb = get_image_size_kb(img)
        if img_size_kb > ctx.config.max_image_size_kb:
            img = resize_image(img, img_size_kb)

        hash_value = str(phash(img, hash_size=16))
        if (
            await ctx.image_repo.get_one(field="hash", value=hash_value)
            is not None
        ):
            logger.error(f"Found duplicate at {img_url}")
            return

        id = str(uuid4())
        output_path = (
            f"{ctx.config.img_dir}/{id}.{ctx.config.img_save_extension}"
        )
        img.save(output_path)

    await ctx.image_repo.add(
        entities.Image(id=id, url=img_url, hash=hash_value, processed=0)
    )
    info.images_scraped += 1


async def process_page_content(
    response_text: str, info: ScraperInfo, amount: int
) -> None:
    soup = BeautifulSoup(response_text, "html.parser")

    for image in soup.select(ctx.config.css_selector):
        if info.images_scraped == amount:
            return
        await process_image(image, info)
