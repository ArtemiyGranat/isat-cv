from typing import ClassVar

from shared.db import Entity


class Image(Entity):
    id: str
    path: str
    hash: str
    processed: int  # bool but SQLite moment

    _pk: ClassVar[str] = "id"
    _table_name: ClassVar[str] = "images"
