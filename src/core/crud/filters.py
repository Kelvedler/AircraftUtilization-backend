from datetime import datetime
from core import schemas


def apply_match(pipeline: list[dict], **fields: str | None) -> None:
    for field, value in fields.items():
        if value:
            pipeline.append({"$match": {field: value}})


def apply_built_interval(
    pipeline: list[dict], built_interval: schemas.BuiltInterval
) -> None:
    built_filter = {}
    if built_interval.built_gte:
        built_min = datetime.combine(built_interval.built_gte, datetime.max.time())
        built_filter["$gte"] = built_min
    if built_interval.built_lte:
        built_max = datetime.combine(built_interval.built_lte, datetime.min.time())
        built_filter["$lte"] = built_max
    if built_filter:
        pipeline.append({"$match": {"built": built_filter}})


def apply_landed_interval(
    pipeline: list[dict], landed_interval: schemas.LandedInterval
) -> None:
    landed_filter = {}
    if landed_interval.landed_gte:
        landed_min = datetime.combine(landed_interval.landed_gte, datetime.min.time())
        landed_filter["$gte"] = landed_min
    if landed_interval.landed_lte:
        landed_max = datetime.combine(landed_interval.landed_lte, datetime.max.time())
        landed_filter["$lte"] = landed_max
    if landed_filter:
        pipeline.append({"$match": {"landed_at": landed_filter}})


def apply_duration_interval(
    pipeline: list[dict], duration_interval: schemas.DurationInterval
) -> None:
    duration_filter = {}
    if duration_interval.duration_gte:
        duration_filter["$gte"] = duration_interval.duration_gte
    if duration_interval.duration_lte:
        duration_filter["$lte"] = duration_interval.duration_lte
    if duration_filter:
        pipeline.append({"$match": {"duration_minutes": duration_filter}})
