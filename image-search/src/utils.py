import numpy as np
import torch
from is_context import ctx
from PIL import Image

from shared.models import Distance


def extract_features(image):
    transformed_image = ctx.transform(image).unsqueeze(0)
    with torch.no_grad():
        features = ctx.model(transformed_image)
    return features.squeeze(0)


async def similar_images(target_file, amount=10):
    target_image = Image.open(target_file).convert("RGB")
    target_features = extract_features(target_image).detach().numpy()

    return [
        image.url
        for image in await ctx.image_repo.get_nearest_embeddings(
            "image_embeddings",
            np.array2string(target_features, separator=", "),
            Distance.COSINE_SIMILARITY,
            amount,
            field="processed",
            value=True,
        )
    ]
