import json
from datetime import datetime, timedelta

import pytest

from app.api.helpers.cache import (
    get_conversion_result_from_cache,
    set_conversion_result_to_cache,
)
from app.core.config import settings
from app.core.connections import redis_cache
from app.schemas.conversion import Currency

headers = {"API-Key": settings.API_KEY_SECRET}


@pytest.mark.asyncio
async def test_set_conversion_result_to_cache(
    raw_conversion_result, redis_connection, redis_test_database
):

    currency = Currency.USD
    await set_conversion_result_to_cache(
        currency, raw_conversion_result=raw_conversion_result
    )
    cache_value = await redis_cache.get(currency.value)
    assert isinstance(cache_value, bytes)
    redis_connection.flushdb()


@pytest.mark.asyncio
async def test_get_conversion_result_from_cache(
    raw_conversion_result, redis_connection, redis_test_database
):

    currency = Currency.USD
    await set_conversion_result_to_cache(
        currency, raw_conversion_result=raw_conversion_result
    )
    cache_value = await get_conversion_result_from_cache(currency)
    assert isinstance(cache_value, dict)
    assert cache_value == raw_conversion_result
    redis_connection.flushdb()


@pytest.mark.asyncio
async def test_cache_invalidation(
    raw_conversion_result, redis_connection, redis_test_database
):

    currency = Currency.USD
    await set_conversion_result_to_cache(
        currency, raw_conversion_result=raw_conversion_result
    )
    cache_value = await redis_cache.get(currency.value)
    value = json.loads(cache_value)
    value["timestamp"] = (datetime.utcnow() - timedelta(1)).isoformat()
    modified_value = value
    modified_value = json.dumps(modified_value)
    await redis_cache.set(currency.value, modified_value)
    # Should get empty dict if cache invalidation algorythm works
    cache_value = await get_conversion_result_from_cache(currency)
    assert cache_value == {}
    redis_connection.flushdb()
