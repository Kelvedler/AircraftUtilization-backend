import math
import logging
from core import schemas
from core.crud.filters import apply_built_interval, apply_match
from core.mongodb import MongodbConn
from core.settings import settings

logger = logging.getLogger(__name__)


def list_exclude_empty(item_list):
    return item_list if item_list != [None] else None


async def get_page(
    page: int,
    model: str | None,
    manufacturer: str | None,
    owner: str | None,
    operator: str | None,
    built_interval: schemas.BuiltInterval,
    db: MongodbConn,
) -> schemas.AircraftPage:
    documents_to_skip = (page - 1) * settings.items_per_page
    pipeline: list[dict] = []
    apply_match(
        pipeline=pipeline,
        model=model,
        manufacturer_icao=manufacturer,
        owner=owner,
        operator=operator,
    )
    apply_built_interval(pipeline=pipeline, built_interval=built_interval)
    pipeline.append(
        {
            "$group": {
                "_id": "$icao24",
                "flights_recorded": {"$count": {}},
                "registration": {"$addToSet": "$registration"},
                "model": {"$addToSet": "$model"},
                "manufacturer_icao": {"$addToSet": "$manufacturer_icao"},
                "owner": {"$addToSet": "$owner"},
                "operator": {"$addToSet": "$operator"},
                "built": {"$addToSet": "$built"},
            }
        }
    )
    pipeline.append({"$sort": {"flights_recorded": -1, "_id": 1}})
    pipeline.append(
        {
            "$facet": {
                "aircraft": [
                    {"$skip": documents_to_skip},
                    {"$limit": settings.items_per_page},
                ],
                "total": [{"$count": "aircraft"}],
            }
        }
    )
    logger.debug(f"Aircraft pipeline: {pipeline}")

    result = next(
        db.flights.aggregate(
            pipeline=pipeline,
        )
    )

    aircraft: list[schemas.Aircraft] = []
    for item in result["aircraft"]:
        aircraft.append(
            schemas.Aircraft(
                icao24=item["_id"],
                flights_recorded=item["flights_recorded"],
                registration=list_exclude_empty(item["registration"]),
                model=list_exclude_empty(item["model"]),
                manufacturer_icao=list_exclude_empty(item["manufacturer_icao"]),
                owner=list_exclude_empty(item["owner"]),
                operator=list_exclude_empty(item["operator"]),
                built=list_exclude_empty(item["built"]),
            )
        )
    total_facet = result["total"]
    results_total = total_facet[0]["aircraft"] if total_facet else 0
    pages_total = math.ceil(results_total / settings.items_per_page)
    return schemas.AircraftPage(results=aircraft, pages_total=pages_total)
