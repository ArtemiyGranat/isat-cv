import io
import logging
from uuid import uuid4

from bs4 import BeautifulSoup
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
    page: int


@retry(stop=stop_after_attempt(7), wait=wait_exponential(multiplier=1, max=60))
async def get_with_retry(url: str) -> Response:
    response = await ctx.http_client.get(url)
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


async def process_image(url: str, info: ScraperInfo) -> None:
    response = await get_with_retry(url)
    if response.status_code != 200:
        logger.error(f"Failed to download image from {url}")
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
            logger.error(f"Found duplicate at {url}")
            return

        id = str(uuid4())
        output_path = (
            f"{ctx.config.img_dir}/{id}.{ctx.config.img_save_extension}"
        )
        img.save(output_path)

    await ctx.image_repo.add(
        entities.Image(
            id=id,
            url=url,
            hash=hash_value,
            mean_h=0,
            mean_s=0,
            mean_v=0,
            mean_l=0,
            mean_a=0,
            mean_b=0,
            processed=0,
        )
    )
    info.images_scraped += 1


async def filter_urls(info, tags):
    image_urls = [image["src"] for image in tags]
    if not image_urls:
        logger.info(f"There is no images on page {info.page}")
        return []

    processed_urls = [
        image.url
        for image in await ctx.image_repo.get_many_from_list(
            field="url", values=image_urls
        )
    ]
    unprocessed_urls = [url for url in image_urls if url not in processed_urls]
    if not unprocessed_urls:
        logger.info(f"All images on page {info.page} already exists")

    return unprocessed_urls


async def process_page_content(
    response_text: str, info: ScraperInfo, amount: int, css_selector
) -> None:
    soup = BeautifulSoup(response_text, "html.parser")
    unprocessed_urls = await filter_urls(info, soup.select(css_selector))
    if not unprocessed_urls:
        return

    for url in unprocessed_urls:
        if info.images_scraped == amount:
            return
        await process_image(url, info)
