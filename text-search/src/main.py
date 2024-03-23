import logging
from contextlib import asynccontextmanager
from typing import List

from context import ctx
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
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
    allow_origins=["*"],
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
