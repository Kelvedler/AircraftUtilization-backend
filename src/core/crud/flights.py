import logging
from datetime import UTC, datetime

import pymongo

from core import schemas
from core.mongodb import MongodbConn
from core.settings import settings
from core.time import to_timestamp

logger = logging.getLogger(__name__)


async def get_page(
    page: int,
    icao24: str | None,
    landed_interval: schemas.LandedInterval,
    duration_interval: schemas.DurationInterval,
    db: MongodbConn,
) -> list[schemas.Flights]:
    filter: dict[str, str | dict[str, datetime] | dict[str, int]] = {}
    if icao24:
        filter["icao24"] = icao24

    landed_at_filter: dict[str, datetime] = {}
    if landed_interval.landed_gte:
        landed_at_filter["$gte"] = datetime.combine(
            landed_interval.landed_gte, datetime.min.time()
        ).replace(tzinfo=UTC)
    if landed_interval.landed_lte:
        landed_at_filter["$lte"] = datetime.combine(
            landed_interval.landed_lte, datetime.max.time()
        ).replace(tzinfo=UTC)

    if landed_at_filter:
        filter["landed_at"] = landed_at_filter

    duration_filter: dict[str, int] = {}
    if duration_interval.duration_gte:
        duration_filter["$gte"] = duration_interval.duration_gte
    if duration_interval.duration_lte:
        duration_filter["$lte"] = duration_interval.duration_lte

    if duration_filter:
        filter["duration_minutes"] = duration_filter

    logger.debug(f"flights filter: {filter}")

    documents_to_skip = (page - 1) * settings.items_per_page
    cursor = db.flights.find(
        filter=filter, skip=documents_to_skip, limit=settings.items_per_page
    ).sort([("landed_at", pymongo.DESCENDING)])

    flights: list[schemas.Flights] = []
    for item in cursor:
        landed_at: datetime = item["landed_at"].replace(tzinfo=UTC)
        flights.append(
            schemas.Flights(
                id=item["_id"],
                icao24=item["icao24"],
                duration_minutes=item["duration_minutes"],
                landed_at=to_timestamp(dt=landed_at),
                manufacturer_icao=item["manufacturer_icao"],
                model=item["model"],
                registration=item["registration"],
                built=item["built"],
                owner=item["owner"],
                operator=item["operator"],
            )
        )
    return flights
