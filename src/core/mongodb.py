import logging
from typing_extensions import Annotated

from fastapi import Depends
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.errors import ServerSelectionTimeoutError

from core.settings import settings

logger = logging.getLogger(__name__)


def get_db() -> Database:
    client: MongoClient = MongoClient(
        host=settings.mongodb.url.host,
        port=settings.mongodb.url.port,
        username=settings.mongodb.url.username,
        password=settings.mongodb.url.password,
        serverSelectionTimeoutMS=3000,
    )
    return client[settings.mongodb.db]


def test_connection() -> None:
    try:
        logger.info("Testing connection")
        get_db().command("ping")
    except ServerSelectionTimeoutError:
        raise ConnectionError("Could not connect to MongoDB")
    else:
        logger.info("Status ok")


MongodbConn = Annotated[Database, Depends(get_db)]
