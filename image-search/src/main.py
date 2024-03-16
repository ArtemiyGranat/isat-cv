import logging
from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, File, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from is_context import ctx
from utils import similar_images

from shared.logger import configure_logging


@asynccontextmanager
async def lifespan(_: FastAPI):
    configure_logging()
    await ctx.init_db()
    try:
        yield
    finally:
        await ctx.dispose_db()


app = FastAPI(lifespan=lifespan)
logger = logging.getLogger("app")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post(
    "/image_search/",
    summary="Search similar images",
    status_code=status.HTTP_200_OK,
)
async def image_search(
    image: UploadFile = File(...), amount: int = 10
) -> List[str]:
    return await similar_images(image.file, amount)


@app.get("/", summary="Check availability")
def healthcheck():
    return "Image search is running!"
