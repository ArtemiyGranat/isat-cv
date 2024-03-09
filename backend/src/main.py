import logging
import os
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, File, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware

from shared.logger import configure_logging


@asynccontextmanager
async def lifespan(_: FastAPI):
    configure_logging()
    try:
        yield
    finally:
        await ctx.close_client()


app = FastAPI(lifespan=lifespan)
logger = logging.getLogger("app")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://0.0.0.0:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Context:
    def __init__(self) -> None:
        self.http_client = httpx.AsyncClient()
        self.scraper_url = os.getenv("SCRAPER_URL")
        self.color_search_url = os.getenv("COLOR_SEARCH_URL")
        self.image_blender_url = os.getenv("IMAGE_BLENDER_URL")

    async def close_client(self) -> None:
        await self.http_client.aclose()


ctx = Context()

# TODO: if service is unavailable give some feedback to frontend


# TODO: Progress? WebSockets?
@app.post(
    "/scrape/{page}/{amount}",
    summary="Scrape certain amount of images",
    status_code=status.HTTP_200_OK,
)
async def scrape(page: int, amount: int) -> None:
    await ctx.http_client.post(
        f"{ctx.scraper_url}/scrape/{page}/{amount}", timeout=None
    )
    return {"message": f"Scraped {amount} images"}


@app.post(
    "/color_search/{color_model}",
    summary="Search images by color",
    status_code=status.HTTP_200_OK,
)
async def color_search(color_model: str, image: UploadFile = File(...)):
    urls = await ctx.http_client.post(
        f"{ctx.color_search_url}/color_search/{color_model}",
        files={"image": (image.file)},
        timeout=None,
    )

    return urls.json()


@app.post(
    "/blend/",
    summary="Blend two images using Laplacian and Gaussian pyramids",
    status_code=status.HTTP_200_OK,
)
async def blend(
    first_image: UploadFile = File(...), second_image: UploadFile = File(...)
):
    await ctx.http_client.post(
        f"{ctx.image_blender_url}/blend",
        files={
            "first_file": (first_image.file),
            "second_file": (second_image.file),
        },
        timeout=None,
    )


@app.get(
    "/text_search/{text}",
    summary="Search images by text",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
)
def text_search():
    return "Not implemented"


@app.get(
    "/image_search/",
    summary="Search images by another image",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
)
def image_search():
    return "Not implemented"


@app.get("/", summary="Check availability")
def healthcheck():
    return "IsatCv is running!"
