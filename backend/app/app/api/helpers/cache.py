import json
from datetime import datetime, timedelta
from logging import getLogger

import aioredis

from app.core.connections import redis_cache
from app.schemas.conversion import Currency

logger = getLogger(__name__)


async def get_conversion_result_from_cache(currency: Currency) -> dict:
    """Checks for conversion result data obtained by another service.
    If there are no data in the cache, returns an empty dict.
    If data is available, first check if data is not outdated yet,
    and if so, invalidates the cache. Otherwise returns the conversion result data,
    inside the cache.

    Cache invalidation mechanism: Time Expiration.

    Algorythm: Based on my understanding from reading
    [this artice](https://support.has-to-be.com/hc/en-us/articles/360005026959-Overview-of-be-ENERGISED-COMMUNITY-tariffs)
    the currency conversion is based on the daily exchange rate of the day on which the charging session was completed,
    so upon requesting, invalidate the cache if it's older than a day.

    Args:
        currency (Currency): [description]

    Returns:
        dict: [description]
    """

    try:
        cache_value: json = await redis_cache.get(currency.value)
    except aioredis.RedisError:  # pragma: no cover # general exception
        return dict()
    if not cache_value:
        return dict()

    cache_value: dict = json.loads(cache_value)
    cached_timestamp: datetime = cache_value.get("timestamp")
    cached_timestamp = datetime.fromisoformat(cached_timestamp)
    # Calculate the next day from the cached_timestamp
    next_day_of_cached = (cached_timestamp + timedelta(days=1)).replace(
        hour=0, minute=0, second=0
    )
    # If it's older than a day, invalidate the cache
    if datetime.utcnow() >= next_day_of_cached:
        await redis_cache.delete(currency.value)
        logger.info(
            "Cache data was outdated, since it got invalidate, currency: %s",
            currency.value,
        )
        return dict()
    logger.info(
        "Reading currency conversion data from cache, currency: %s", currency.value
    )
    return cache_value.get("data")


async def set_conversion_result_to_cache(
    currency: Currency, raw_conversion_result: dict
) -> None:
    """Store currency convert data in cache.
    Default expiration time is 24 hours.
    Also store timestamp from the time the cache is created,
    to later user for cache invalidation.

    Args:
        currency (Currency): Used as the key for the key/value store
        raw_conversion_result (dict): Conversion data provided by a service
    """

    timestamp = datetime.utcnow().isoformat()
    cache_value = json.dumps({"timestamp": timestamp, "data": raw_conversion_result})
    try:
        await redis_cache.execute(
            "set", currency.value, cache_value, "ex", twenty_four := 24 * 3600
        )
    except aioredis.RedisError:  # pragma: no cover # general exception
        return
    logger.info("New currency convert data is cached, %s", currency.value)
