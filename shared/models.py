import json
from typing import List
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
    hsv: List[float] | None = None
    lab: List[float] | None = None
