import logging
import os
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware

from shared.logger import configure_logging


@asynccontextmanager
async def lifespan(_: FastAPI):
    configure_logging()
    yield
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

    async def close_client(self) -> None:
        await self.http_client.aclose()


ctx = Context()


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


@app.get("/", summary="Hello, world")
def hello():
    return "Hello, world!"
