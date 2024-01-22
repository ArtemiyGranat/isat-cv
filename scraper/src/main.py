import logging
import os
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup
from fastapi import FastAPI

app = FastAPI()
logger = logging.getLogger("app")

# TODO: take start url, css selector etc from config
START_URL = ""
TOTAL_PAGES = 1
IMG_DIRECTORY = ""
CSS_SELECTOR = ""


@app.post("/scrape/{amount}", summary="Scrape certain amount of images")
def scrape(amount: int):
    os.makedirs(IMG_DIRECTORY, exist_ok=True)

    scraped = 0
    response = httpx.get(START_URL)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        images = soup.select(CSS_SELECTOR)

        for image in images:
            if scraped == amount:
                logger.info(f"Scraped {amount} images")
                return

            url = urljoin(START_URL, image["src"])
            image_response = httpx.get(url)

            if image_response.status_code == 200:
                if not url.endswith(".jpg"):
                    url = url + ".jpg"
                image_filename = os.path.join(IMG_DIRECTORY, os.path.basename(url))
                if os.path.exists(image_filename):
                    logger.info(f"{url} already exists")
                    continue

                with open(image_filename, "wb") as f:
                    f.write(image_response.content)
                logger.info(f"Downloaded: {image_filename}")
                scraped += 1
            else:
                logger.error(f"Failed to download image from {url}")


# TODO
@app.get("/images/{amount}", summary="Get certain amount of images")
def get_images(amount: int):
    return amount
