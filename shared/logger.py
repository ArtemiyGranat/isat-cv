import json
from logging.config import dictConfig

from shared.resources import CONFIG_PATH


def configure_logging() -> None:
    with open(CONFIG_PATH) as f:
        d = json.load(f)
        dictConfig(d["logger"])
