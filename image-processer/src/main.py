import asyncio
import logging
import os
from typing import List

import rembg
import torch
import torchvision.models as models
import torchvision.transforms as transforms
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from databases import Database
from PIL import Image

import shared.entities as entities
from shared.color import ColorModel, compute_mean_color
from shared.db import SqliteRepository, gen_sqlite_address
from shared.logger import configure_logging
from shared.resources import CONFIG_PATH, SharedResources

logger = logging.getLogger("app")


class Context:
    def __init__(self) -> None:
        shared_resources = SharedResources(CONFIG_PATH)

        self.config = shared_resources.img_processer

        self.tensors_dir = self.config.tensors_dir
        self.session = rembg.new_session(self.config.rembg_model)

        self.orig_img_dir = shared_resources.scraper.img_dir
        self.orig_img_ext = shared_resources.scraper.img_save_extension

        self.sqlite = Database(
            gen_sqlite_address(shared_resources.sqlite_creds)
        )
        self.image_repo = SqliteRepository(self.sqlite, entities.Image)

        self.transform = transforms.Compose(
            [
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
                ),
            ]
        )
        self.model = models.resnet18(pretrained=True)

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
    with Image.open(
        f"{ctx.orig_img_dir}/{image.id}.{ctx.orig_img_ext}"
    ) as orig_img:
        processed_img = rembg.remove(orig_img, session=ctx.session)
        mean_hsv = compute_mean_color(processed_img, ColorModel.HSV)
        mean_lab = compute_mean_color(processed_img, ColorModel.LAB)

        transformed_image = ctx.transform(orig_img).unsqueeze(0)
        with torch.no_grad():
            features = ctx.model(transformed_image)
        torch.save(features.squeeze(0), f"{ctx.tensors_dir}/{image.id}.pt")
        logger.info(f"Saved tensor to {ctx.tensors_dir}/{image.id}.pt")

        processed_img.save(f"{ctx.config.img_dir}/{image.id}.png")

    await ctx.image_repo.update(
        entity=entities.Image(
            id=image.id,
            url=image.url,
            hash=image.hash,
            mean_h=mean_hsv[0],
            mean_s=mean_hsv[1],
            mean_v=mean_hsv[2],
            mean_l=mean_lab[0],
            mean_a=mean_lab[1],
            mean_b=mean_lab[2],
            processed=1,
        ),
        fields=[
            "processed",
            "mean_h",
            "mean_s",
            "mean_v",
            "mean_l",
            "mean_a",
            "mean_b",
        ],
    )
    logger.info(
        f"Processed image: {ctx.orig_img_dir}/{image.id}.{ctx.orig_img_ext}"
    )


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
