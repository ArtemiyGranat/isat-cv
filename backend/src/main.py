import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
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
