from typing import ClassVar
from uuid import UUID

from shared.db import Entity


class Image(Entity):
    id: UUID
    path: str
    hash: str

    _pk: ClassVar[str] = "id"
    _table_name: ClassVar[str] = "images"
