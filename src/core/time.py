from datetime import datetime


def to_timestamp(dt: datetime) -> int:
    return int(round(dt.timestamp()))
