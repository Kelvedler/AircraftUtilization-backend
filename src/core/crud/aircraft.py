from typing import List

from core import schemas
from core.mongodb import MongodbConn
from core.settings import settings


async def get_page(page: int, db: MongodbConn) -> List[schemas.Aircraft]:
    documents_to_skip = (page - 1) * settings.items_per_page
    cursor = db.flights.aggregate(
        pipeline=[
            {"$group": {"_id": "$icao24", "flights_recorded": {"$sum": 1}}},
            {"$sort": {"flights_recorded": -1, "_id": 1}},
            {"$skip": documents_to_skip},
            {"$limit": settings.items_per_page},
        ],
    )

    aircraft: List[schemas.Aircraft] = []
    for item in cursor:
        aircraft.append(
            schemas.Aircraft(
                icao24=item["_id"], flights_recorded=item["flights_recorded"]
            )
        )
    return aircraft
