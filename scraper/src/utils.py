import io
import logging
from uuid import uuid4

from bs4 import Tag
from context import ctx
from imagehash import phash
from PIL import Image
from pydantic import BaseModel
from tenacity import retry, stop_after_attempt

import shared.entities as entities

logger = logging.getLogger("app")


class ScraperInfo(BaseModel):
    images_scraped: int


@retry(stop=stop_after_attempt(7))
async def get_with_retry(url: str):
    return await ctx.http_client.get(url)


async def process_image(image: Tag, info: ScraperInfo) -> int:
    if (
        await ctx.image_repo.get_one(field="path", value=image["src"])
        is not None
    ):
        logger.info(f"{image['src']} already exists")
        return

    response = await get_with_retry(image["src"])
    if response.status_code != 200:
        logger.error(f"Failed to download image from {image['src']}")
        return

    hash = str(phash(Image.open(io.BytesIO(response.content)), hash_size=16))
    if await ctx.image_repo.get_one(field="hash", value=hash) is not None:
        logger.error(f"Found duplicate at {image['src']}")
        return

    id = str(uuid4())
    path = f"{ctx.config.img_dir}/{id}.jpg"
    with open(path, "wb") as f:
        f.write(response.content)

    await ctx.image_repo.add(
        entities.Image(id=id, path=image["src"], hash=hash)
    )
    info.images_scraped += 1
