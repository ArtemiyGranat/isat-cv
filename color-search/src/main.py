import logging
from contextlib import asynccontextmanager

from cs_context import ctx
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from shared.logger import configure_logging


@asynccontextmanager
async def lifespan(_: FastAPI):
    configure_logging()
    await ctx.init_db()
    await ctx.image_repo.create_table()
    yield
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
    "/color-search/{type}",
    summary="Get 10 images with complementary median image color",
    status_code=status.HTTP_200_OK,
)
async def color_search(page: int, amount: int) -> None:
    if type == "hsv":
        return "hsv"
    elif type == "lab":
        return "lab"

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Unknown color search type, available types is 'hsv' and 'lab'",
    )


@app.get("/", summary="Check availability")
async def healthcheck():
    return "Color search is available!"
