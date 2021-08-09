import asyncio
import json
from datetime import datetime, timedelta
from unittest import mock

import aioredis
import pytest
from fastapi.testclient import TestClient

from app.api.helpers.cache import (
    get_conversion_result_from_cache,
    set_conversion_result_to_cache,
)
from app.core.config import settings
from app.schemas.conversion import Currency

headers = {"API-Key": settings.API_KEY_SECRET}


async def async_magic():
    pass


# Monkey patch MagicMock to test it in code blocks with await keyword
mock.MagicMock.__await__ = lambda x: async_magic().__await__()


@mock.patch("app.main.app.redis.execute")
@mock.patch("app.main.app.redis.get")
def test_currency_conversion_cache_get(
    mocked_redis_get, mocked_redis_set, client: TestClient, clear_cache
) -> None:

    r = client.get(
        f"{settings.API_V1_STR}/rate/converted-rate/",
        headers=headers,
        params=[
            ("overall", 10),
            ("energy", 4),
            ("time", 3),
            ("transaction", 3),
            ("currency", "USD"),
        ],
    )
    assert r.status_code == 200
    assert mocked_redis_get.called

    result = r.json()

    # Means that external API not working
    # and returning default currency
    # hence caching is not a matter
    if not result.get("currency") == "EUR":  # pragma: no cover
        assert mocked_redis_set.called


@pytest.mark.asyncio
async def test_set_conversion_result_to_cache(raw_conversion_result, redis_connection):
    from app.main import app, startup

    await startup()

    currency = Currency.USD
    await set_conversion_result_to_cache(
        currency, raw_conversion_result=raw_conversion_result
    )
    cache_value = await app.redis.get(currency.value)
    assert isinstance(cache_value, bytes)
    redis_connection.flushdb()


@pytest.mark.asyncio
async def test_get_conversion_result_from_cache(
    raw_conversion_result, redis_connection
):
    from app.main import app, startup

    await startup()

    currency = Currency.USD
    await set_conversion_result_to_cache(
        currency, raw_conversion_result=raw_conversion_result
    )
    cache_value = await get_conversion_result_from_cache(currency)
    assert isinstance(cache_value, dict)
    assert cache_value == raw_conversion_result
    redis_connection.flushdb()


@pytest.mark.asyncio
async def test_cache_invalidation(raw_conversion_result, redis_connection):
    from app.main import app, startup

    await startup()

    currency = Currency.USD
    await set_conversion_result_to_cache(
        currency, raw_conversion_result=raw_conversion_result
    )
    cache_value = await app.redis.get(currency.value)
    value = json.loads(cache_value)
    value["timestamp"] = (datetime.utcnow() - timedelta(1)).isoformat()
    modified_value = value
    modified_value = json.dumps(modified_value)
    await app.redis.set(currency.value, modified_value)
    # Should get empty dict if cache invalidation algorythm works
    cache_value = await get_conversion_result_from_cache(currency)
    assert cache_value == {}
    redis_connection.flushdb()
