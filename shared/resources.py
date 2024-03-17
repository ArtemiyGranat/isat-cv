from pydantic import BaseModel

from shared.models import JSONSettings


class DatabaseCredentials(BaseModel):
    driver: str
    db_name: str


class PgCredentials(DatabaseCredentials):
    username: str
    password: str
    url: str
    port: str


class ScraperSettings(BaseModel):
    img_dir: str
    total_pages: int
    max_image_size_kb: int
    img_save_extension: str


class ImgProcesserSettings(BaseModel):
    interval: int
    img_dir: str


class ModelNames(BaseModel):
    rembg_model: str
    clip_model: str


class ImgBlenderSettings(BaseModel):
    pyramids_levels: int


class BackendSettings(BaseModel):
    timeout: int


class SharedResources(JSONSettings):
    pg_creds: PgCredentials
    scraper: ScraperSettings
    img_processer: ImgProcesserSettings
    img_blender: ImgBlenderSettings
    ml_model_names: ModelNames
    backend: BackendSettings | None = None


CONFIG_PATH = "config/config.json"
