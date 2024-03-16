import clip
import numpy as np
from ts_context import ctx


async def find_similar_images(query: str, amount: int = 10):
    text = clip.tokenize([query]).to(ctx.device)
    text_features = ctx.model.encode_text(text).detach().squeeze(0).numpy()

    return [
        image.url
        for image in await ctx.image_repo.get_nearest_embeddings(
            "text_embeddings",
            np.array2string(text_features, separator=", "),
            ctx.image_repo.distance_query,
            amount,
            field="processed",
            value=True,
        )
    ]
