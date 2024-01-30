from apscheduler.schedulers.asyncio import AsyncIOScheduler
from databases import Database

from shared.db import SqliteRepository, gen_sqlite_address
from shared.entities import Image
from shared.resources import SharedResources


class Context:
    def __init__(self):
        shared_resources = SharedResources("config/config.json")

        self.interval = shared_resources.img_processer.interval
        self.sqlite = Database(
            gen_sqlite_address(shared_resources.sqlite_creds)
        )
        self.image_repo = SqliteRepository(self.sqlite, Image)

    async def init_db(self) -> None:
        await self.sqlite.connect()

    async def dispose_db(self) -> None:
        await self.sqlite.disconnect()

    def init_scheduler(self, func):
        self.scheduler = AsyncIOScheduler()
        self.scheduler.add_job(
            func,
            "interval",
            seconds=self.interval,
        )


ctx = Context()
