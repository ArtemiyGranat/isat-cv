import logging
from contextlib import asynccontextmanager

from context import ctx
from fastapi import FastAPI, HTTPException
from tenacity import RetryError
from utils import ScraperInfo, get_with_retry, process_page_content

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


@app.post(
    "/scrape/{page}/{amount}",
    summary="Scrape certain amount of images",
    status_code=204,
)
async def scrape(page: int, amount: int) -> None:
    info = ScraperInfo(images_scraped=0)
    while info.images_scraped < amount and page < ctx.config.total_pages:
        try:
            response = await get_with_retry(f"{ctx.config.start_url}{page}")
            page += 1
            if response.status_code != 200:
                continue

            await process_page_content(response.text, info, amount)
        except RetryError:
            raise HTTPException(
                status_code=524,
                detail=f"Failed to scrape images from page {page}, try again later",
            )
    logger.info(f"Scraped {amount} images")
