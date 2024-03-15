import torchvision.models as models
import torchvision.transforms as transforms
from databases import Database

from shared.db import PgRepository, gen_db_address
from shared.entities import Image
from shared.resources import CONFIG_PATH, SharedResources


# TODO: same as for cs_context
class Context:
    def __init__(self) -> None:
        shared_resources = SharedResources(CONFIG_PATH)

        self.pg = Database(gen_db_address(shared_resources.pg_creds))
        self.image_repo = PgRepository(self.pg, Image)

        # TODO: move tensors_dir to somewhere else? looks not good
        self.tensors_dir = (
            shared_resources.img_processer.img_search_tensors_dir
        )

        self.model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
        self.model.eval()

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
        await self.pg.connect()

    async def dispose_db(self) -> None:
        await self.pg.disconnect()


ctx = Context()
