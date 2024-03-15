import logging
from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from ts_context import ctx
from utils import find_similar_images

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
    "/text_search/",
    summary="Search images by text",
    status_code=status.HTTP_200_OK,
)
async def text_search(query: str, amount: int = 10) -> List[str]:
    return await find_similar_images(query, amount)


@app.get("/", summary="Check availability")
def healthcheck():
    return "Text search is running!"
