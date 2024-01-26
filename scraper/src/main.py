import logging
import os
import time
from contextlib import asynccontextmanager

import httpx
from bs4 import BeautifulSoup
from context import ctx
from fastapi import FastAPI
from utils import ScraperInfo, process_image

from shared.logger import configure_logging


@asynccontextmanager
async def lifespan(_: FastAPI):
    configure_logging()
    yield


app = FastAPI(lifespan=lifespan)
logger = logging.getLogger("app")


@app.post("/scrape/{amount}", summary="Scrape certain amount of images")
def scrape(amount: int) -> None:
    os.makedirs(ctx.config.img_dir, exist_ok=True)

    info = ScraperInfo()
    page = 1
    while info.images_scraped < amount and page < ctx.config.total_pages:
        try:
            response = ctx.http_client.get(f"{ctx.config.start_url}{page}")
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")

                for image in soup.select(ctx.config.css_selector):
                    if info.images_scraped == amount:
                        logger.info(f"Scraped {amount} images")
                        return

                    process_image(image, info)
                    # tenacity
                    time.sleep(0.1)
            time.sleep(0.1)
            page += 1
        # retry
        except httpx.TimeoutException:
            time.sleep(1)


# TODO
@app.get("/images/{amount}", summary="Get certain amount of images")
def get_images(amount: int) -> int:
    return amount
