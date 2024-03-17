import clip
from ts_context import ctx

from shared.models import Distance


async def find_similar_images(query: str, amount: int = 10):
    text = clip.tokenize([query]).to(ctx.device)
    text_features = ctx.model.encode_text(text).detach().squeeze(0).numpy()

    return [
        image.url
        for image in await ctx.image_repo.get_nearest_embeddings(
            "text_embeddings",
            text_features,
            Distance.COSINE_SIMILARITY,
            amount,
            field="processed",
            value=True,
        )
    ]
