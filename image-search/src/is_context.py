import torchvision.models as models
import torchvision.transforms as transforms
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

        # TODO: move tensors_dir to somewhere else? looks not good
        self.tensors_dir = shared_resources.img_processer.tensors_dir

        # TODO: it shouldn't be just models.resnet18, save it or idk
        # FIXME: UserWarning: The parameter 'pretrained' is deprecated since 0.13 and may be removed in the future, please use 'weights' instead.
        self.model = models.resnet18(pretrained=True)
        self.transform = transforms.Compose(
            [
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
                ),
            ]
        )

    async def init_db(self) -> None:
        await self.sqlite.connect()

    async def dispose_db(self) -> None:
        await self.sqlite.disconnect()


ctx = Context()
