from databases import Database

from shared.db import PgRepository, gen_db_address
from shared.entities import Image
from shared.resources import CONFIG_PATH, SharedResources


# TODO: cs_context name is not the best I guess
class Context:
    def __init__(self) -> None:
        shared_resources = SharedResources(CONFIG_PATH)

        self.pg = Database(gen_db_address(shared_resources.pg_creds))
        self.image_repo = PgRepository(self.pg, Image)

    async def init_db(self) -> None:
        await self.pg.connect()

    async def dispose_db(self) -> None:
        await self.pg.disconnect()


ctx = Context()
