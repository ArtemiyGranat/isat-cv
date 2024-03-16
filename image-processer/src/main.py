import asyncio
import logging
import os

import clip
import numpy as np
import rembg
import torch
import torchvision.models as models
import torchvision.transforms as transforms
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from databases import Database
from PIL import Image

import shared.entities as entities
from shared.color import ColorModel, compute_mean_color
from shared.db import PgRepository, gen_db_address
from shared.logger import configure_logging
from shared.resources import CONFIG_PATH, SharedResources

logger = logging.getLogger("app")


class Context:
    def __init__(self) -> None:
        shared_resources = SharedResources(CONFIG_PATH)
        model_names = shared_resources.ml_model_names

        self.config = shared_resources.img_processer

        self.session = rembg.new_session(model_names.rembg_model)

        self.orig_img_dir = shared_resources.scraper.img_dir
        self.orig_img_ext = shared_resources.scraper.img_save_extension

        self.pg = Database(gen_db_address(shared_resources.pg_creds))
        self.image_repo = PgRepository(self.pg, entities.Image)

        self.image_search_transform = transforms.Compose(
            [
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
                ),
            ]
        )
        self.image_search_model = models.resnet18(
            weights=models.ResNet18_Weights.DEFAULT
        )

        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.text_search_model, self.text_search_preprocess = clip.load(
            model_names.clip_model, device=self.device
        )

    async def init_db(self) -> None:
        await self.pg.connect()

    async def dispose_db(self) -> None:
        await self.pg.disconnect()

    def init_scheduler(self, func) -> None:
        self.scheduler = AsyncIOScheduler()
        self.scheduler.add_job(
            func, "interval", seconds=self.config.interval, args=[self]
        )


def compute_image_search_tensors(ctx: Context, img: Image) -> None:
    transformed_image = ctx.image_search_transform(img).unsqueeze(0)
    with torch.no_grad():
        features = ctx.image_search_model(transformed_image)

    return features.squeeze(0)


def compute_text_search_tensors(ctx: Context, img: Image) -> None:
    transformed_image = (
        ctx.text_search_preprocess(img).unsqueeze(0).to(ctx.device)
    )
    with torch.no_grad():
        features = ctx.text_search_model.encode_image(transformed_image)

    return features.squeeze(0)


async def process_image(ctx: Context, image: entities.Image) -> None:
    with Image.open(
        f"{ctx.orig_img_dir}/{image.id}.{ctx.orig_img_ext}"
    ) as orig_img:
        processed_img = rembg.remove(orig_img, session=ctx.session)
        mean_hsv = compute_mean_color(processed_img, ColorModel.HSV)
        mean_lab = compute_mean_color(processed_img, ColorModel.LAB)

        image_embeddings = compute_image_search_tensors(
            ctx, processed_img.convert("RGB")
        )
        text_embeddings = compute_text_search_tensors(ctx, processed_img)

        processed_img.save(f"{ctx.config.img_dir}/{image.id}.png")

    await ctx.image_repo.update(
        entity=entities.Image(
            id=image.id,
            url=image.url,
            hash=image.hash,
            hsv=mean_hsv,
            lab=mean_lab,
            image_embeddings=np.array2string(
                image_embeddings.numpy(), separator=", "
            ),
            text_embeddings=np.array2string(
                text_embeddings.numpy(), separator=", "
            ),
            processed=True,
        ),
        fields=[
            "processed",
            "hsv",
            "lab",
            "image_embeddings",
            "text_embeddings",
        ],
    )

    logger.info(
        f"Processed image: {ctx.orig_img_dir}/{image.id}.{ctx.orig_img_ext}"
    )


async def process_images(ctx: Context) -> None:
    for image in await ctx.image_repo.get_many(field="processed", value=False):
        await process_image(ctx, image)


async def main():
    ctx = Context()
    ctx.image_search_model.eval()
    ctx.text_search_model.eval()

    os.makedirs(ctx.config.img_dir, exist_ok=True)

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
