import json
from enum import Enum

from pydantic import BaseModel


class JSONSettings(BaseModel):
    def __init__(self, path: str):
        with open(path, "r") as f:
            config = json.load(f)
            return super().__init__(**config)


class ColorModel(int, Enum):
    LAB = 0
    HSV = 1


class Distance(int, Enum):
    COSINE_SIMILARITY = 0
    DISTANCE = 1
    INNER_PRODUCT = 2
