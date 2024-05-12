from datetime import UTC, datetime
from typing import List, Union

import pymongo

from core import schemas
from core.mongodb import MongodbConn
from core.settings import settings
from core.time import to_timestamp


async def get_page(
    page: int,
    icao24: Union[str, None],
    landed_interval: schemas.LandedInterval,
    duration_interval: schemas.DurationInterval,
    db: MongodbConn,
) -> List[schemas.Flights]:
    filter = {}
    if icao24:
        filter["icao24"] = icao24

    landed_at_filter = {}
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

    duration_filter = {}
    if duration_interval.duration_gte:
        duration_filter["$gte"] = duration_interval.duration_gte
    if duration_interval.duration_lte:
        duration_filter["$lte"] = duration_interval.duration_lte

    if duration_filter:
        filter["duration_minutes"] = duration_filter

    documents_to_skip = (page - 1) * settings.items_per_page
    cursor = db.flights.find(
        filter=filter, skip=documents_to_skip, limit=settings.items_per_page
    ).sort([("landed_at", pymongo.DESCENDING)])

    flights: List[schemas.Flights] = []
    for item in cursor:
        landed_at: datetime = item["landed_at"].replace(tzinfo=UTC)
        flights.append(
            schemas.Flights(
                id=item["_id"],
                icao24=item["icao24"],
                duration_minutes=item["duration_minutes"],
                landed_at=to_timestamp(dt=landed_at),
            )
        )
    return flights