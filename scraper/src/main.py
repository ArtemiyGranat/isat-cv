import logging
from contextlib import asynccontextmanager

from context import ctx
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from tenacity import RetryError
from utils import ScraperInfo, get_with_retry, process_page_content

from shared.logger import configure_logging


@asynccontextmanager
async def lifespan(_: FastAPI):
    configure_logging()
    await ctx.init_db()
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
    "/scrape/{page}/{amount}",
    summary="Scrape certain amount of images",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def scrape(
    page: int,
    amount: int,
    start_url: str | None = ctx.default_start_url,
    css_selector: str = ctx.default_css_selector,
) -> None:
    if start_url is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Start URL is not specified either in request or on server",
        )

    info = ScraperInfo(images_scraped=0, page=page)
    while info.images_scraped < amount and info.page < ctx.config.total_pages:
        try:
            response = await get_with_retry(f"{start_url}{info.page}")
            if response.status_code != 200:
                info.page += 1
                logger.info(f"Page {info.page} cannot be retrieved")
                continue

            await process_page_content(
                response.text, info, amount, css_selector
            )
            info.page += 1
        except RetryError:
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail=f"Failed to scrape images from page {info.page}",
            )
    logger.info(f"Scraped {amount} images")


@app.get("/", summary="Check availability")
async def healthcheck():
    return "Scraper is running!"
