import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from shared.logger import configure_logging


@asynccontextmanager
async def lifespan(_: FastAPI):
    configure_logging()


app = FastAPI(lifespan=lifespan)
logger = logging.getLogger("app")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[],  # TODO
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", summary="Hello, world")
def hello():
    return "Hello, world!"
