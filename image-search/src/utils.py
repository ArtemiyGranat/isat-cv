import torch
from is_context import ctx
from PIL import Image
from scipy.spatial.distance import cosine


def extract_features(image):
    transformed_image = ctx.transform(image).unsqueeze(0)
    with torch.no_grad():
        features = ctx.model(transformed_image)
    return features.squeeze(0)


async def similar_images(target_file, amount=10):
    ctx.model.eval()

    target_image = Image.open(target_file).convert("RGB")
    target_features = extract_features(target_image)
    similarities = []

    images = await ctx.image_repo.get_many(field="processed", value=1)
    for image in images:
        features = torch.load(
            f"{ctx.tensors_dir}/{image.id}.pt", weights_only=True
        )

        similarity = 1 - cosine(target_features.numpy(), features.numpy())
        similarities.append((similarity, image.url))

    similarities.sort(reverse=True)

    return [url for _, url in similarities[:amount]]
