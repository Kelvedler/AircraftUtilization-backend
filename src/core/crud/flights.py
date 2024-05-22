from datetime import UTC, datetime
import logging
import math

from core import schemas
from core.crud.filters import (
    apply_duration_interval,
    apply_landed_interval,
    apply_match,
)
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
    apply_match(
        pipeline=pipeline,
        icao24=icao24,
        model=model,
        manufacturer_icao=manufacturer,
        owner=owner,
        operator=operator,
    )
    apply_landed_interval(pipeline=pipeline, landed_interval=landed_interval)
    apply_duration_interval(pipeline=pipeline, duration_interval=duration_interval)
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
