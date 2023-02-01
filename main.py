import logging
from typing import Any, Dict

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from google.cloud import bigquery
from starlette.middleware import Middleware
from starlette_context import plugins
from starlette_context.middleware import RawContextMiddleware

from utils.exception_handler import fastapi_exception_logging_handler
from utils.gcloud_logging import gcloud_logging

gcloud_logging.setup_gcloud_logger()

middleware = [
    Middleware(
        RawContextMiddleware,
        plugins=(plugins.RequestIdPlugin(), plugins.CorrelationIdPlugin()),
    )
]


app = FastAPI(
    middleware=middleware,
    exception_handlers={
        # this catch all errors, logs them and re-raises
        Exception: fastapi_exception_logging_handler,  # type: ignore
    },
)


@app.get("/")
def root() -> JSONResponse:
    return JSONResponse(content={"content": "hello world"})


@app.get("/test-logging/")
def test_logging() -> JSONResponse:
    logging.info(gcloud_logging.task_invocation_link)
    logging.debug("this is debug")
    logging.info("this is info")
    logging.warning("this is warning")
    logging.error("this is an error")
    raise ZeroDivisionError("don't divide by zero kids")


@app.get("/test-bq/")
def test_bq() -> JSONResponse:
    client = bigquery.Client()
    query_job = client.query(
        "select customer_id, emailable_customer from offers.audience_marketable limit 10"
    )
    rows = query_job.result()
    res = []
    for row in rows:
        output: Dict[str, Any] = {
            "customer_id": row["customer_id"],
            "emailable": row["emailable_customer"],
        }
        res.append(output)
    return JSONResponse(content={"status": res})
