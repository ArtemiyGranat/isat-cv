import clip
import torch
from databases import Database

from shared.db import SqliteRepository, gen_sqlite_address
from shared.entities import Image
from shared.resources import CONFIG_PATH, SharedResources


# TODO: same as for cs_context
class Context:
    def __init__(self) -> None:
        shared_resources = SharedResources(CONFIG_PATH)

        self.sqlite = Database(
            gen_sqlite_address(shared_resources.sqlite_creds)
        )
        self.image_repo = SqliteRepository(self.sqlite, Image)

        # TODO: vector storage
        self.tensors_dir = (
            shared_resources.img_processer.text_search_tensors_dir
        )

        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model, self.preprocess = clip.load(
            shared_resources.ml_model_names.clip_model, device=self.device
        )

    async def init_db(self) -> None:
        await self.sqlite.connect()

    async def dispose_db(self) -> None:
        await self.sqlite.disconnect()


ctx = Context()
