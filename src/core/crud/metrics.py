from decimal import Decimal
import logging

from core import schemas
from core.crud.filters import apply_built_interval, apply_landed_interval, apply_match
from core.mongodb import MongodbConn

logger = logging.getLogger(__name__)


async def operator_get_page(
    operators: list[str],
    owner: str | None,
    built_interval: schemas.BuiltInterval,
    landed_interval: schemas.LandedInterval,
    db: MongodbConn,
) -> list[schemas.OperatorMetric]:
    pipeline: list[dict] = [{"$match": {"operator": {"$in": operators}}}]
    apply_match(pipeline=pipeline, owner=owner)
    apply_built_interval(pipeline=pipeline, built_interval=built_interval)
    apply_landed_interval(pipeline=pipeline, landed_interval=landed_interval)
    pipeline.append(
        {
            "$group": {
                "_id": "$operator",
                "fleet": {"$addToSet": "$icao24"},
                "models": {"$addToSet": "$model"},
                "flights_recorded": {"$count": {}},
                "flight_duration_avg": {"$avg": "$duration_minutes"},
                "flight_days": {"$addToSet": {"$dayOfYear": "$landed_at"}},
            }
        }
    )
    pipeline.append(
        {
            "$project": {
                "_id": 1,
                "fleet_size": {"$size": "$fleet"},
                "models": 1,
                "flights_recorded": 1,
                "flight_duration_avg": 1,
                "cycles_per_day": {
                    "$cond": [
                        {"$eq": [{"$size": "$flight_days"}, 0]},
                        0,
                        {"$divide": ["$flights_recorded", {"$size": "$flight_days"}]},
                    ]
                },
            }
        }
    )
    pipeline.append({"$sort": {"fleet": -1, "_id": 1}})

    logger.debug(f"Operators pipeline: {pipeline}")

    cursor = db.flights.aggregate(pipeline=pipeline)
    operator_metrics: list[schemas.OperatorMetric] = []
    for item in cursor:
        operator_metrics.append(
            schemas.OperatorMetric(
                operator=item["_id"],
                fleet_size=item["fleet_size"],
                models=[i for i in item["models"] if isinstance(i, str)],
                flights_recorded=item["flights_recorded"],
                flight_duration_avg=round(Decimal(item["flight_duration_avg"]), 2),
                cycles_per_day=round(Decimal(item["cycles_per_day"]), 2),
            )
        )

    return operator_metrics
