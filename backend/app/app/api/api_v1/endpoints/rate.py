from fastapi import APIRouter, Body, Depends
from fastapi.security.api_key import APIKey

from app.api.helpers import calculate_rate, validate_meters, validate_timestamps
from app.core.security import get_api_key
from app.schemas import CDR, Rate, RateResult

router = APIRouter()


@router.post("/rate/", tags=["rate"], response_model=RateResult)
async def apply_rate(
    api_key: APIKey = Depends(get_api_key),
    rate: Rate = Body(..., embed=True),
    cdr: CDR = Body(..., embed=True),
) -> RateResult:
    """Base API for applying rate to a CDR.
    Uses seperation of concerns design pattern, check or modify functions for
    different concerns.

    Args:
        api_key (APIKey): Uses security backend for api key authorization, receives
        the api key through header.
        rate (Rate): Rate components body.
        cdr (CDR): CDR components body.

    Returns:
        [JSON]: Calculated rates.
    """

    total_seconds = await validate_timestamps(
        start=cdr.timestamp_start, stop=cdr.timestamp_stop
    )
    total_kwh = await validate_meters(start=cdr.meter_start, stop=cdr.meter_stop)
    overall, energy, time, transaction = await calculate_rate(
        total_seconds=total_seconds,
        total_kwh=total_kwh,
        energy_rate=rate.energy,
        time_rate=rate.time,
        transaction_rate=rate.transaction,
    )

    return {
        "overall": overall,
        "components": {"energy": energy, "time": time, "transaction": transaction},
    }
