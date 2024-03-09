import io
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, Response, UploadFile, status
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


# TODO: routes.py in shared?


@app.post(
    "/blend/",
    summary="Blend two images using Laplacian and Gaussian pyramids",
    status_code=status.HTTP_200_OK,
    responses={200: {"content": {"image/png": {}}}},
    response_class=Response,
)
async def blend(
    first_image: UploadFile = File(...), second_image: UploadFile = File(...)
) -> None:
    blended_image = blend_images(first_image.file, second_image.file)

    # TODO: Find a way to do this more elegant
    byte_arr = io.BytesIO()
    blended_image.save(byte_arr, format="PNG")
    byte_arr.seek(0)
    return Response(content=byte_arr.getvalue(), media_type="image/png")


@app.get("/", summary="Check availability")
def healthcheck():
    return "Image blender is running!"
