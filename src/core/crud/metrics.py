from datetime import datetime
from decimal import Decimal
import logging

from core import schemas
from core.mongodb import MongodbConn

logger = logging.getLogger(__name__)


async def operator_get_page(
    operators: list[str],
    owner: str | None,
    built_interval: schemas.BuiltInterval,
    db: MongodbConn,
) -> list[schemas.OperatorMetric]:
    pipeline: list[dict] = [{"$match": {"operator": {"$in": operators}}}]
    if owner:
        pipeline.append({"$match": {"owner": owner}})
    built_filter = {}
    if built_interval.built_gte:
        built_min = datetime.combine(built_interval.built_gte, datetime.max.time())
        built_filter["$gte"] = built_min
    if built_interval.built_lte:
        built_max = datetime.combine(built_interval.built_lte, datetime.min.time())
        built_filter["$lte"] = built_max
    if built_filter:
        pipeline.append({"$match": {"built": built_filter}})
    pipeline.append(
        {
            "$group": {
                "_id": "$operator",
                "fleet": {"$addToSet": "$icao24"},
                "models": {"$addToSet": "$model"},
                "flights_recorded": {"$count": {}},
                "flight_duration_avg": {"$avg": "$duration_minutes"},
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
            )
        )

    return operator_metrics
