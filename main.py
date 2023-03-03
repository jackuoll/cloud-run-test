import logging
import time

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from utils.gcloud_logging import gcloud_logging

gcloud_logging.setup_gcloud_logger()


app = FastAPI()


@app.get("/")
def root() -> JSONResponse:
    two_hours_in_seconds = 60 * 60 * 2
    for i in range(two_hours_in_seconds):
        logging.info(f"It has been {i}")
        time.sleep(1)
    return JSONResponse(content={"content": "hello world"})


@app.get("/die")
def memkiller() -> JSONResponse:
    blah = ["we're all going to die, aren't we?"]
    while True:
        blah.extend(blah)
    return JSONResponse(content={"stop": "i'm already dead"})
