from contextlib import asynccontextmanager
import logging.config
from typing import Any, AsyncGenerator

from fastapi import FastAPI

from core.mongodb import test_connection as mongodb_test_connection
from core.postgres import test_connection as postgres_test_connection
from core.settings import log_config


def startup() -> None:
    logging.config.dictConfig(config=log_config)
    mongodb_test_connection()
    postgres_test_connection()


def shutdown() -> None:
    pass


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, Any]:
    startup()
    yield
    shutdown()
