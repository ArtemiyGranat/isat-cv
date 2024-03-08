import logging
from contextlib import asynccontextmanager

from cs_context import ctx
from fastapi import FastAPI, File, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from utils import similar_color

from shared.color import ColorModel
from shared.logger import configure_logging


@asynccontextmanager
async def lifespan(_: FastAPI):
    configure_logging()
    await ctx.init_db()
    await ctx.image_repo.create_table()
    try:
        yield
    finally:
        await ctx.close_client()
        await ctx.dispose_db()


app = FastAPI(lifespan=lifespan)
logger = logging.getLogger("app")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://0.0.0.0:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post(
    "/color_search/{color_model}",
    summary="Get images with complementary median image color",
    status_code=status.HTTP_200_OK,
)
async def color_search(
    color_model: str, image: UploadFile = File(...), amount: int = 10
) -> None:
    if color_model not in ["hsv", "lab"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unknown color model, available models is 'hsv' and 'lab'",
        )

    color_model = ColorModel.LAB if color_model == "lab" else ColorModel.HSV
    return await similar_color(image.file, color_model, amount)


@app.get("/", summary="Check availability")
async def healthcheck():
    return "Color search is available!"
