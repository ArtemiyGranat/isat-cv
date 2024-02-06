import io
import logging
import time
from uuid import uuid4

from bs4 import BeautifulSoup
from context import ctx
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
async def get_with_retry(url: str):
    response = await ctx.http_client.get(url)
    time.sleep(0.25)
    return response


async def process_image(url: str, info: ScraperInfo) -> int:
    response = await get_with_retry(url)
    if response.status_code != 200:
        logger.error(f"Failed to download image from {url}")
        return

    hash = str(phash(Image.open(io.BytesIO(response.content)), hash_size=16))
    if await ctx.image_repo.get_one(field="hash", value=hash) is not None:
        logger.error(f"Found duplicate at {url}")
        return

    id = str(uuid4())
    path = f"{ctx.config.img_dir}/{id}.jpg"
    with open(path, "wb") as f:
        f.write(response.content)

    await ctx.image_repo.add(entities.Image(id=id, path=url, hash=hash))
    info.images_scraped += 1


async def process_page_content(
    response_text: str, info: ScraperInfo, amount: int
) -> None:
    soup = BeautifulSoup(response_text, "html.parser")

    image_urls = [
        image["src"] for image in soup.select(ctx.config.css_selector)
    ]
    processed_urls = [
        image.path
        for image in await ctx.image_repo.get_many_from_list(
            field="path", values=image_urls
        )
    ]
    unprocessed_urls = [url for url in image_urls if url not in processed_urls]
    if not unprocessed_urls:
        logger.info("All images on page {info.page} already exists")
        return

    for url in unprocessed_urls:
        if info.images_scraped == amount:
            return
        await process_image(url, info)
