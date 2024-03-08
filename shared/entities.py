from typing import ClassVar

from shared.db import Entity


class Image(Entity):
    id: str
    url: str
    hash: str
    mean_h: float
    mean_s: float
    mean_v: float
    mean_l: float
    mean_a: float
    mean_b: float
    processed: int  # bool but SQLite moment

    _pk: ClassVar[str] = "id"
    _table_name: ClassVar[str] = "images"
