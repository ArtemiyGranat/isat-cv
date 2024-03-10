import clip
import torch
from ts_context import ctx


async def find_similar_images(query: str, amount: int = 10):
    text = clip.tokenize([query]).to(ctx.device)
    text_features = ctx.model.encode_text(text)

    similarities = []

    for image in await ctx.image_repo.get_many(field="processed", value=1):
        image_features = torch.load(
            f"{ctx.tensors_dir}/{image.id}.pt", weights_only=True
        )

        with torch.no_grad():
            similarity = (image_features @ text_features.T).cpu().numpy()
            similarities.append((similarity[0][0], image.url))

    similarities.sort(reverse=True)

    return [url for _, url in similarities[:amount]]
