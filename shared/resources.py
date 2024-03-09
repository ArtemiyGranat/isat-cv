from pydantic import BaseModel

from shared.models import JSONSettings


class DatabaseCredentials(BaseModel):
    driver: str
    db_name: str
    username: str | None = None
    password: str | None = None
    url: str | None = None
    port: int | None = None


class ScraperSettings(BaseModel):
    start_url: str  # start_url should be url ends with something like ?page=
    css_selector: str
    img_dir: str
    total_pages: int
    max_image_size_kb: int
    img_save_extension: str


class ImgProcesserSettings(BaseModel):
    interval: int
    img_dir: str
    rembg_model: str
    tensors_dir: str


class ImgBlenderSettings(BaseModel):
    pyramids_levels: int


class SharedResources(JSONSettings):
    sqlite_creds: DatabaseCredentials
    scraper: ScraperSettings
    img_processer: ImgProcesserSettings
    img_blender: ImgBlenderSettings


CONFIG_PATH = "config/config.json"
