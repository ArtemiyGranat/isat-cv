from typing import ClassVar, List
from uuid import UUID

from shared.db import Entity


class Image(Entity):
    id: UUID
    url: str
    hash: str
    hsv: List[float] | None = None
    lab: List[float] | None = None
    image_embeddings: List[float] | None = None
    text_embeddings: List[float] | None = None
    processed: bool

    _pk: ClassVar[str] = "id"
    _table_name: ClassVar[str] = "images"
