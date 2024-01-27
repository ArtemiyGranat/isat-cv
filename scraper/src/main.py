import logging
import os
import time
from contextlib import asynccontextmanager

from bs4 import BeautifulSoup
from context import ctx
from fastapi import FastAPI, HTTPException
from tenacity import RetryError
from utils import ScraperInfo, get_with_retry, process_image

from shared.logger import configure_logging


@asynccontextmanager
async def lifespan(_: FastAPI):
    configure_logging()
    await ctx.init_db()
    await ctx.image_repo.create_table()
    yield
    await ctx.dispose_db()
    await ctx.close_client()


app = FastAPI(lifespan=lifespan)
logger = logging.getLogger("app")


@app.post("/scrape/{page}/{amount}", summary="Scrape certain amount of images")
async def scrape(page: int, amount: int) -> None:
    os.makedirs(ctx.config.img_dir, exist_ok=True)

    info = ScraperInfo(images_scraped=0)
    while info.images_scraped < amount and page < ctx.config.total_pages:
        try:
            response = await get_with_retry(f"{ctx.config.start_url}{page}")
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")

                for image in soup.select(ctx.config.css_selector):
                    if info.images_scraped == amount:
                        logger.info(f"Scraped {amount} images")
                        return

                    await process_image(image, info)
                    time.sleep(0.1)
            time.sleep(0.1)
            page += 1
        except RetryError:
            raise HTTPException(
                status_code=524,
                detail=f"Failed to scrape images from page {page}, try again later",
            )


# TODO
@app.get("/images/{amount}", summary="Get certain amount of images")
def get_images(amount: int) -> int:
    return amount
