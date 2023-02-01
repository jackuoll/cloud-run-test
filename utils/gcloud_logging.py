import logging
import logging.config
import random
import string
import warnings
from typing import Optional

import colorlog
import google.cloud.logging
from google.cloud.logging.handlers import CloudLoggingHandler
from starlette_context import context
from starlette_context.errors import ContextDoesNotExistError

from utils.settings import SETTINGS, Environment, Settings

WARNINGS_MESSAGES_TO_SUPPRESS = [
    "Your application has authenticated using end user credentials",
]
WARNINGS_MODULES_TO_SUPPRESS = [
    "aiohttp.helpers",
]

DEFAULT_LOGGER_NAME = ""
CONSOLE_FORMAT = "%(asctime)s [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s"

logging.config.dictConfig(
    {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {"standard": {"format": CONSOLE_FORMAT}},
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "INFO",
                "formatter": "standard",
                "stream": "ext://sys.stdout",
            },
        },
        "loggers": {
            DEFAULT_LOGGER_NAME: {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": True,
            },
        },
    }
)

for warning_message in WARNINGS_MESSAGES_TO_SUPPRESS:
    warnings.filterwarnings("ignore", warning_message)

for warning_module in WARNINGS_MODULES_TO_SUPPRESS:
    warnings.filterwarnings("ignore", module=warning_module)


class GCLHandler(CloudLoggingHandler):
    def emit(self, record) -> None:  # type: ignore
        try:
            request_id: str = str(context.get("X-Request-ID"))
            msg = self.format(record)
            self.transport.send(
                record,
                msg,
                resource=self.resource,
                labels={**self.labels, **{"request_id": request_id}},
            )
        except ContextDoesNotExistError:
            super().emit(record)


class GCloudLogging:
    def __init__(self) -> None:
        instance_id_charset = string.hexdigits
        eight_random_characters = [
            random.choice(instance_id_charset).lower() for _ in range(8)
        ]
        # save `self.instance_id` as part of class instance, in case we need it later for reporting
        self.instance_id = "".join(eight_random_characters)
        self._settings: Optional["Settings"] = None
        self.labels = {"instance_id": self.instance_id}
        self._handler: Optional[GCLHandler] = None

    @property
    def handler(self) -> Optional[GCLHandler]:
        if (
            self.settings.environment == Environment.local
            and not self.settings.force_gcloud_logging
        ):
            return None
        elif self._handler is None:
            client = google.cloud.logging.Client(project=self.settings.project)
            handler_name = (
                f"{self.settings.application}-{self.settings.environment.value}"
            )
            self._handler = GCLHandler(client, name=handler_name, labels=self.labels)
        return self._handler

    @property
    def settings(self) -> "Settings":
        if not self._settings:
            self._settings = SETTINGS
        return self._settings

    def _logs_query_link(self, query: str) -> str:
        current_project = self.settings.project
        return f"https://console.cloud.google.com/logs/query;query={query}?project={current_project}"

    @property
    def task_instance_gcl_link(self) -> str:
        """
        :return: A url string which is a link to python logs of this specific task run
        """
        return self._logs_query_link(
            query=f"labels.instance_id%3D%22{self.instance_id}%22"
        )

    @property
    def task_invocation_link(self) -> Optional[str]:
        try:
            request_id: str = context.get("X-Request-ID", "")
            return self._logs_query_link(
                query=f"labels.request_id%3D%22{request_id}%22"
            )
        except ContextDoesNotExistError:
            return None

    def task_instance_label_link(self, label_key: str, label_value: str) -> str:
        return self._logs_query_link(query=f"labels.{label_key}%3D%22{label_value}%22")

    def setup_gcloud_logger(self) -> None:
        """
        Add a Google Cloud logger so python logs will be visible at `https://console.cloud.google.com/logs/`
        """
        if self.handler is None:
            return

        # add a google cloud logging handler at INFO level or above
        default_logger = logging.getLogger(DEFAULT_LOGGER_NAME)
        # it would be nice to set this to debug, but we need to exclude gcloud logger itself as it generates
        # a very large amount of spam
        default_logger.setLevel(logging.INFO)
        default_logger.addHandler(self.handler)
        logging.info(
            f"Instantiated Google Cloud logging handler with labels: {self.labels}\n"
            f"Task instance logs available at {self.task_instance_gcl_link}"
        )


def set_console_colours_in_default_handler() -> None:
    """
    Set the console colours for when we run CLI locally and want easy to see warnings & errors
    """
    default_logger = logging.getLogger(DEFAULT_LOGGER_NAME)
    for handler in default_logger.handlers:
        if handler.name == "console":
            colours = dict(colorlog.default_log_colors)
            colours.update({"INFO": "white"})
            handler.formatter = colorlog.ColoredFormatter(
                f"%(log_color)s{CONSOLE_FORMAT}", log_colors=colours
            )


gcloud_logging = GCloudLogging()
