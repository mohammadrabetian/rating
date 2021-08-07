import contextlib
from logging import getLogger

from fastapi import APIRouter, Depends, Query
from fastapi.security.api_key import APIKey

from app.core.config import settings
from app.core.security import get_api_key
from app.schemas import ConvertedRateResult, Currency

router = APIRouter()

import aiohttp
import ujson

logger = getLogger(__name__)
session = aiohttp.ClientSession(json_serialize=ujson.dumps)
EXCHANGE_API = "https://api.exchangerate.host/convert?from={0}&to={1}&amount={2}"


@router.get("/conversion/", response_model=ConvertedRateResult)
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
    of implementation, for a more robust system, an app should minimise
    relying on third parties.

    Note: Default input currency is assumed to be EUR


    Args:
        overall (float)
        energy (float)
        time (float)
        transaction (float)
        currency (Currency): Currency to be converted into.

    Returns:
        [JSON]: Converted rate | Default input rate
    """
    conversion_result = dict()
    response = dict()
    rate_convert_api = EXCHANGE_API.format(
        settings.DEFAULT_CURRENCY, currency.value, overall
    )

    # Suppress exceptions (better alternative for try/except/pass)
    with contextlib.suppress(aiohttp.ClientError):
        async with session.get(rate_convert_api, timeout=2) as convertion_response:
            conversion_result = await convertion_response.json()

    if conversion_result and conversion_result.get("result"):
        conversaion_rate = conversion_result.get("info").get("rate")
        converted_overall_rate = conversion_result.get("result")
        overall = (
            "{0:0.2f}".format(converted_overall_rate)
            if not converted_overall_rate.is_integer()
            else converted_overall_rate
        )
        converted_energy, converted_time, converted_transaction = map(
            lambda rate: rate * conversaion_rate, [energy, time, transaction]
        )
        energy, time, transaction = map(
            lambda rate: "{0:0.3f}".format(rate)
            if not rate.is_integer()
            else int(rate),
            [converted_energy, converted_time, converted_transaction],
        )
        response = {
            "overall": overall,
            "components": {"energy": energy, "time": time, "transaction": transaction},
            "currency": currency,
        }
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
