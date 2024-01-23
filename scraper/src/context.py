import httpx

from shared.resources import SharedResources


class Context:
    def __init__(self):
        self.config = SharedResources("config/config.json").scraper
        self.http_client = httpx.Client()


ctx = Context()
