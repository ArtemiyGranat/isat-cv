import logging
import os
from contextlib import asynccontextmanager
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from context import ctx
from fastapi import FastAPI

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
        response = ctx.http_client.get(f"{ctx.config.start_url}{page}")
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            images = soup.select(ctx.config.css_selector)

            for image in images:
                if scraped == amount:
                    logger.info(f"Scraped {amount} images")
                    return

                url = urljoin(ctx.config.start_url, image["src"])
                if os.path.splitext(url) == "":
                    url = url + ".jpg"
                img_name = os.path.join(
                    ctx.config.img_dir, os.path.basename(url)
                )
                if os.path.exists(img_name):
                    logger.info(f"{url} already exists")
                    continue

                image_response = ctx.http_client.get(url)

                if image_response.status_code == 200:
                    with open(img_name, "wb") as f:
                        f.write(image_response.content)
                    scraped += 1
                else:
                    logger.error(f"Failed to download image from {url}")
        page += 1


# TODO
@app.get("/images/{amount}", summary="Get certain amount of images")
def get_images(amount: int) -> int:
    return amount
