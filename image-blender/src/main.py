import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from utils import blend_images

from shared.logger import configure_logging


@asynccontextmanager
async def lifespan(_: FastAPI):
    configure_logging()
    yield


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


@app.post(
    "/blend/",
    summary="Blend two images using Laplacian and Gaussian pyramids",
    status_code=status.HTTP_200_OK,
)
async def color_search(
    first_image: UploadFile = File(...), second_image: UploadFile = File(...)
) -> None:
    blend_images(first_image.file, second_image.file)
    pass


@app.get("/", summary="Check availability")
def healthcheck():
    return "Image blender is running!"
