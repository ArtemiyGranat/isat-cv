import logging
import os
from contextlib import asynccontextmanager
from typing import Dict

import httpx
from fastapi import FastAPI, File, Response, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware

from shared.logger import configure_logging
from shared.resources import CONFIG_PATH, SharedResources


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
        "*",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Context:
    def __init__(self) -> None:
        shared_resources = SharedResources(CONFIG_PATH)
        self.timeout = getattr(shared_resources.backend, "timeout", None)

        self.http_client = httpx.AsyncClient()
        self.scraper_url = os.getenv("SCRAPER_URL")
        self.color_search_url = os.getenv("COLOR_SEARCH_URL")
        self.image_blender_url = os.getenv("IMAGE_BLENDER_URL")
        self.image_search_url = os.getenv("IMAGE_SEARCH_URL")
        self.text_search_url = os.getenv("TEXT_SEARCH_URL")

    async def close_client(self) -> None:
        await self.http_client.aclose()


ctx = Context()

# TODO: if service is unavailable give some feedback to frontend

# TODO: split into files?


# TODO: Progress? WebSockets?
@app.post(
    "/scrape/{page}/{amount}",
    summary="Scrape certain amount of images",
    status_code=status.HTTP_200_OK,
)
async def scrape(page: int, amount: int) -> Dict[str, str]:
    await ctx.http_client.post(
        f"{ctx.scraper_url}/scrape/{page}/{amount}", timeout=ctx.timeout
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
        timeout=ctx.timeout,
    )

    return urls.json()


@app.post(
    "/blend/",
    summary="Blend two images using Laplacian and Gaussian pyramids",
    status_code=status.HTTP_200_OK,
    responses={200: {"content": {"image/png": {}}}},
    response_class=Response,
)
async def blend(
    first_image: UploadFile = File(...), second_image: UploadFile = File(...)
):
    blended_image = await ctx.http_client.post(
        f"{ctx.image_blender_url}/blend/",
        files={
            "first_image": (first_image.file),
            "second_image": (second_image.file),
        },
        timeout=ctx.timeout,
    )

    return Response(content=blended_image.content, media_type="image/png")


@app.post(
    "/text_search/",
    summary="Search images by text",
    status_code=status.HTTP_200_OK,
)
async def text_search(query: str):
    urls = await ctx.http_client.post(
        f"{ctx.text_search_url}/text_search/",
        params={"query": query},
        timeout=ctx.timeout,
    )

    return urls.json()


@app.post(
    "/image_search/",
    summary="Search images by image",
    status_code=status.HTTP_200_OK,
)
async def image_search(image: UploadFile = File(...)):
    urls = await ctx.http_client.post(
        f"{ctx.image_search_url}/image_search/",
        files={"image": (image.file)},
        timeout=ctx.timeout,
    )

    return urls.json()


@app.get("/", summary="Check availability")
def healthcheck():
    return "IsatCv is running!"
