import json
from uuid import UUID

from pydantic import BaseModel


class JSONSettings(BaseModel):
    def __init__(self, path: str):
        with open(path, "r") as f:
            config = json.load(f)
            return super().__init__(**config)


class Image(BaseModel):
    id: UUID
    url: str
    hash: str
    processed: int  # bool but SQLite moment
