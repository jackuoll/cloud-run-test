import logging

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette import status

from utils.gcloud_logging import gcloud_logging


async def fastapi_exception_logging_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    logging.exception("Error occurred")
    if gcloud_logging.handler is None:
        raise
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Uncaught exception. See logs for details.",
            "logs_link": gcloud_logging.task_invocation_link,
        },
    )
