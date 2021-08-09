from datetime import datetime

from app.core.exception import bad_request, wrong_isoformat


async def validate_timestamps(start: str, stop: str) -> int:
    """Validator function and convertor for timestamps

    1 - Validation check for timestamps to be of type ISO 8601
    2 - Convert timestamps from isoformat to python datetime format
    3 - Validation check for the correctness of time entries(order and equality)

    Args:
        start (str) charging start timestamp
        stop (str) charging stop timestamp

    Returns:
        [int]: Integer of total seconds

    Raises:
        HTTPException
    """
    try:
        timestamp_start, timestamp_stop = map(
            lambda timestamp: datetime.fromisoformat(timestamp.replace("Z", "+00:00")),
            [start, stop],
        )
    except (ValueError, TypeError, AttributeError):
        return wrong_isoformat()
    if timestamp_start >= timestamp_stop:
        return bad_request(
            err="timestamp_stop cannot be before timestamp_start or be equal"
        )
    return (timestamp_stop - timestamp_start).seconds


async def validate_meters(start: int, stop: int) -> float:
    """Validate meters and convert Wh to kWh"""
    if not stop > start:
        return bad_request(
            err="meter_start cannot be greater than meter_stop or be equal!"
        )
    watt_hour = stop - start
    return watt_hour / 1000
