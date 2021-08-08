from datetime import datetime, timedelta
from numbers import Number

import pytest
from fastapi import HTTPException

from app.api.helpers import validate_meters, validate_timestamps


@pytest.mark.asyncio
async def test_validate_meters_wrong_input() -> None:
    with pytest.raises(HTTPException):
        await validate_meters(start=2, stop=1)


@pytest.mark.asyncio
async def test_validate_meters_correct_input() -> None:
    start = 10000
    stop = 20000
    result = await validate_meters(start=start, stop=stop)
    assert isinstance(result, Number)
    expected_result = (stop - start) / 1000
    assert result == expected_result


@pytest.mark.asyncio
async def test_validate_timestamps_wrong_input_type() -> None:
    with pytest.raises(HTTPException):
        await validate_timestamps(start=datetime.now(), stop=datetime.now())


@pytest.mark.asyncio
async def test_validate_timestamps_wrong_order_logic() -> None:
    now = datetime.now().isoformat()
    two_hours_later = (datetime.now() + timedelta(hours=2)).isoformat()
    with pytest.raises(HTTPException):
        await validate_timestamps(start=two_hours_later, stop=now)


@pytest.mark.asyncio
async def test_validate_timestamps_right_input() -> None:
    now = datetime.now().isoformat()
    two_hours_later = (datetime.now() + timedelta(hours=2)).isoformat()
    result = await validate_timestamps(start=now, stop=two_hours_later)
    assert isinstance(result, Number)
    expected_result = (
        datetime.fromisoformat(two_hours_later) - datetime.fromisoformat(now)
    ).seconds
    assert result == expected_result
