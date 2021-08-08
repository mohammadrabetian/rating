import contextlib
from logging import getLogger

import aiohttp
import ujson
from fastapi import APIRouter, Body, Depends, Query
from fastapi.security.api_key import APIKey

from app.api.helpers import (
    calculate_rate,
    convert_currency,
    get_conversion_result_from_cache,
    set_conversion_result_to_cache,
    validate_meters,
    validate_timestamps,
)
from app.core.config import settings
from app.core.security import get_api_key
from app.schemas import CDR, ConvertedRateResult, Currency, Rate, RateResult

router = APIRouter()
logger = getLogger(__name__)

session = aiohttp.ClientSession(json_serialize=ujson.dumps)
EXCHANGE_API = "https://api.exchangerate.host/convert?from={0}&to={1}"


@router.post("/rate/", response_model=RateResult)
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


@router.get("/rate/converted-rate/", response_model=ConvertedRateResult)
async def apply_conversion(
    api_key: APIKey = Depends(get_api_key),
    overall: float = Query(..., gt=0),
    energy: float = Query(..., gt=0),
    time: float = Query(..., gt=0),
    transaction: float = Query(..., gt=0),
    currency: Currency = Query(default=Currency.USD),
) -> ConvertedRateResult:
    """API for converting rates to another currency.
    Uses the free https://exchangerate.host service for the simplicity
    of implementation.

    Note: Default input currency is assumed to be EUR


    Args:
        overall (float)
        energy (float)
        time (float)
        transaction (float)
        currency (Currency): Currency to be converted into.

    Returns:
        [JSON]: Converted rate | Default input rate

    **Technical Details:**
    The first time you send a request to this API, it will ask the
    https://exchangerate.host service for currency conversion data, calculates conversions,
    and then caches the rate in which it has received from the service. Susequent requests,
    to this endpoint for the same currency will result to reading the rate from cache and,
    caclculating conversions with the cached rate.
    For details on the cache invalidation mechanism, check `get_conversion_result_from_cache` docs.

    """

    raw_conversion_result: dict = await get_conversion_result_from_cache(
        currency=currency
    )
    if raw_conversion_result:
        response = await convert_currency(
            raw_conversion_result=raw_conversion_result,
            overall=overall,
            currency=currency,
            energy=energy,
            time=time,
            transaction=transaction,
        )
        return response

    response = dict()
    rate_convert_api = EXCHANGE_API.format(settings.DEFAULT_CURRENCY, currency.value)

    # Suppress exceptions (better alternative for try/except/pass)
    with contextlib.suppress(aiohttp.ClientError):
        async with session.get(rate_convert_api, timeout=2) as convertion_response:
            raw_conversion_result = await convertion_response.json()

    if raw_conversion_result and raw_conversion_result.get("result"):
        response = await convert_currency(
            raw_conversion_result=raw_conversion_result,
            overall=overall,
            currency=currency,
            energy=energy,
            time=time,
            transaction=transaction,
        )
        await set_conversion_result_to_cache(
            currency=currency, raw_conversion_result=raw_conversion_result
        )
    # If the service isn't available, return the default input currency
    else:
        logger.warning(
            "Currency conversion API is not working, currency: %s", currency.value
        )
        response = {
            "overall": overall,
            "components": {"energy": energy, "time": time, "transaction": transaction},
            "currency": Currency.EUR,
        }
    return response
