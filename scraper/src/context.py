import os

import httpx
from databases import Database

from shared.db import SqliteRepository, gen_sqlite_address
from shared.entities import Image
from shared.resources import CONFIG_PATH, SharedResources


class Context:
    def __init__(self) -> None:
        shared_resources = SharedResources(CONFIG_PATH)

        self.config = shared_resources.scraper

        self.default_start_url = os.getenv("START_URL_SCRAPER")
        self.default_css_selector = os.getenv("CSS_SELECTOR_SCRAPER", "img")

        os.makedirs(self.config.img_dir, exist_ok=True)

        self.sqlite = Database(
            gen_sqlite_address(shared_resources.sqlite_creds)
        )
        self.http_client = httpx.AsyncClient()
        self.image_repo = SqliteRepository(self.sqlite, Image)

    async def init_db(self) -> None:
        await self.sqlite.connect()

    async def dispose_db(self) -> None:
        await self.sqlite.disconnect()

    async def close_client(self) -> None:
        await self.http_client.aclose()


ctx = Context()
