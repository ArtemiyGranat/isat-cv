import asyncio
import logging
import os
from typing import List

import rembg
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from databases import Database
from PIL import Image

import shared.entities as entities
from shared.db import SqliteRepository, gen_sqlite_address
from shared.logger import configure_logging
from shared.resources import SharedResources

logger = logging.getLogger("app")


class Context:
    def __init__(self) -> None:
        shared_resources = SharedResources("config/config.json")

        self.config = shared_resources.img_processer
        self.orig_img_dir = shared_resources.scraper.img_dir
        self.sqlite = Database(
            gen_sqlite_address(shared_resources.sqlite_creds)
        )
        self.image_repo = SqliteRepository(self.sqlite, entities.Image)

    async def init_db(self) -> None:
        await self.sqlite.connect()

    async def dispose_db(self) -> None:
        await self.sqlite.disconnect()

    def init_scheduler(self, func) -> None:
        self.scheduler = AsyncIOScheduler()
        self.scheduler.add_job(
            func, "interval", seconds=self.config.interval, args=[self]
        )


async def process_image(ctx: Context, image: entities.Image) -> None:
    with Image.open(f"{ctx.orig_img_dir}/{image.id}.jpg") as orig_img:
        processed_img = rembg.remove(orig_img)
        processed_img.save(f"{ctx.config.img_dir}/{image.id}.png")

    await ctx.image_repo.update(
        entity=entities.Image(
            id=image.id, url=image.url, hash=image.hash, processed=1
        ),
        fields=["processed"],
    )
    logger.info(f"Removed background: {ctx.orig_img_dir}/{image.id}.jpg")


async def process_images(ctx: Context) -> None:
    images: List[entities.Image] = await ctx.image_repo.get_many(
        field="processed", value=0
    )
    for image in images:
        await process_image(ctx, image)


async def main():
    ctx = Context()
    if not os.path.exists(ctx.config.img_dir):
        os.makedirs(ctx.config.img_dir)

    configure_logging()
    await ctx.init_db()
    ctx.init_scheduler(process_images)

    ctx.scheduler.start()
    try:
        await asyncio.Future()
    except (KeyboardInterrupt, SystemExit, asyncio.exceptions.CancelledError):
        pass
    except Exception as e:
        logger.error(f"An error occured: {e}")
    finally:
        logger.info("The image processing service has been stopped")
        ctx.scheduler.shutdown()
        await ctx.dispose_db()


if __name__ == "__main__":
    asyncio.run(main())