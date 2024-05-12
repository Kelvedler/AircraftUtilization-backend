import logging
from typing import Any, Generator

from sqlalchemy import create_engine
from sqlalchemy.orm.session import Session, sessionmaker
from sqlalchemy.sql.expression import text
from sqlalchemy.exc import OperationalError

from core.settings import settings

logger = logging.getLogger(__name__)

engine = create_engine(url=settings.postgres_url.__str__())

SessionLocal = sessionmaker(bind=engine)


def get_db() -> Generator[Session, Any, Any]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_connection() -> None:
    session = next(get_db())
    try:
        logger.info("Testing connection")
        session.execute(text("SELECT 1"))
    except OperationalError:
        raise ConnectionError("Could not connect to PostgreSQL")
    else:
        logger.info("Status ok")
