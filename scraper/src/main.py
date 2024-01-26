import logging
import os
import time
from contextlib import asynccontextmanager

import httpx
from bs4 import BeautifulSoup
from context import ctx
from fastapi import FastAPI
from process import process_image

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

    scraped = 0
    page = 1
    while scraped < amount and page < ctx.config.total_pages:
        try:
            response = ctx.http_client.get(f"{ctx.config.start_url}{page}")
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")

                for image in soup.select(ctx.config.css_selector):
                    if scraped == amount:
                        logger.info(f"Scraped {amount} images")
                        return

                    status_code = process_image(image)
                    if status_code == 200:
                        scraped += 1

                    time.sleep(0.1)
            time.sleep(0.1)
            page += 1
        except httpx.TimeoutException:
            time.sleep(1)


# TODO
@app.get("/images/{amount}", summary="Get certain amount of images")
def get_images(amount: int) -> int:
    return amount
