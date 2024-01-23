from pydantic import BaseModel

from shared.models import JSONSettings


class ScraperSettings(BaseModel):
    start_url: str  # start_url should be url ends with something like ?page=
    css_selector: str
    img_dir: str
    total_pages: int


class SharedResources(JSONSettings):
    scraper: ScraperSettings
