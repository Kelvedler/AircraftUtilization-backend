from datetime import UTC, datetime
import logging
import math

from core import schemas
from core.mongodb import MongodbConn
from core.settings import settings
from core.time import to_timestamp

logger = logging.getLogger(__name__)


async def get_page(
    page: int,
    icao24: str | None,
    model: str | None,
    manufacturer: str | None,
    owner: str | None,
    operator: str | None,
    landed_interval: schemas.LandedInterval,
    duration_interval: schemas.DurationInterval,
    db: MongodbConn,
) -> schemas.FlightsPage:
    documents_to_skip = (page - 1) * settings.items_per_page
    pipeline: list[dict] = []
    if icao24:
        pipeline.append({"$match": {"icao24": icao24}})
    if model:
        pipeline.append({"$match": {"model": model}})
    if manufacturer:
        pipeline.append({"$match": {"manufacturer_icao": manufacturer}})
    if owner:
        pipeline.append({"$match": {"owner": owner}})
    if operator:
        pipeline.append({"$match": {"operator": operator}})
    landed_filter = {}
    duration_filter = {}
    match: dict[str, dict[str, int] | dict[str, datetime]] = {}
    if landed_interval.landed_gte:
        landed_min = datetime.combine(landed_interval.landed_gte, datetime.min.time())
        landed_filter["$gte"] = landed_min
    if landed_interval.landed_lte:
        landed_max = datetime.combine(landed_interval.landed_lte, datetime.max.time())
        landed_filter["$lte"] = landed_max
    if landed_filter:
        match["landed_at"] = landed_filter

    if duration_interval.duration_gte:
        duration_filter["$gte"] = duration_interval.duration_gte
    if duration_interval.duration_lte:
        duration_filter["$lte"] = duration_interval.duration_lte
    if duration_filter:
        match["duration_minutes"] = duration_filter

    if match:
        pipeline.append({"$match": match})

    pipeline.append(
        {
            "$facet": {
                "flights": [
                    {"$skip": documents_to_skip},
                    {"$limit": settings.items_per_page},
                ],
                "total": [{"$count": "flights"}],
            }
        }
    )

    logger.debug(f"Flights pipeline: {pipeline}")

    result = next(db.flights.aggregate(pipeline=pipeline))
    flights: list[schemas.Flights] = []
    for item in result["flights"]:
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
    total_facet = result["total"]
    results_total = total_facet[0]["flights"] if total_facet else 0
    pages_total = math.ceil(results_total / settings.items_per_page)
    return schemas.FlightsPage(results=flights, pages_total=pages_total)
