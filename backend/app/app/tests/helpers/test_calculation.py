import ast
from decimal import Decimal

import pytest

from app.api.helpers import calculate_rate

total_seconds = 4096
total_kwh = 10.9
energy_rate = 0.3
time_rate = 2
transaction_rate = 1.278


@pytest.mark.asyncio
async def test_calculate_rate_all_float_number() -> None:
    overall, energy, time, transaction = await calculate_rate(
        total_seconds=total_seconds,
        total_kwh=total_kwh,
        energy_rate=energy_rate,
        time_rate=time_rate,
        transaction_rate=transaction_rate,
    )
    assert all(
        list(
            map(
                lambda x: not ast.literal_eval(x).is_integer(),
                [overall, energy, time, transaction],
            )
        )
    )


@pytest.mark.asyncio
async def test_calculate_rate_all_float_number_decimal_points_precision() -> None:
    overall, energy, time, transaction = await calculate_rate(
        total_seconds=total_seconds,
        total_kwh=total_kwh,
        energy_rate=energy_rate,
        time_rate=time_rate,
        transaction_rate=transaction_rate,
    )

    overall_decimal_points_precision = Decimal(overall).as_tuple().exponent
    assert overall_decimal_points_precision == -2
    # Components with the precision of 3
    assert all(
        list(
            map(
                lambda x: x == -3,
                [
                    Decimal(component).as_tuple().exponent
                    for component in [energy, time, transaction]
                ],
            )
        )
    )


@pytest.mark.asyncio
async def test_calculate_rate_all_whole_number() -> None:
    total_seconds = 3600
    total_kwh = 10
    energy_rate = 1
    time_rate = 1
    transaction_rate = 1
    overall, energy, time, transaction = await calculate_rate(
        total_seconds=total_seconds,
        total_kwh=total_kwh,
        energy_rate=energy_rate,
        time_rate=time_rate,
        transaction_rate=transaction_rate,
    )
    assert all(
        map(lambda x: float(x).is_integer(), [overall, energy, time, transaction])
    )
