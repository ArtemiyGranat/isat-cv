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
    await ctx.image_repo.create_table()
    yield
    await ctx.close_client()
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
    "/scrape/{page}/{amount}",
    summary="Scrape certain amount of images",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def scrape(page: int, amount: int) -> None:
    info = ScraperInfo(images_scraped=0, page=page)
    while info.images_scraped < amount and info.page < ctx.config.total_pages:
        try:
            response = await get_with_retry(
                f"{ctx.config.start_url}{info.page}"
            )
            if response.status_code != 200:
                info.page += 1
                logger.info(f"Page {info.page} cannot be retrieved")
                continue

            await process_page_content(response.text, info, amount)
            info.page += 1
        except RetryError:
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail=f"Failed to scrape images from page {info.page}",
            )
    logger.info(f"Scraped {amount} images")
