from enum import Enum

from .rate import RateResult


class Currency(Enum):
    USD = "USD"
    GBP = "GBP"
    JPY = "JPY"
    CAD = "CAD"


class ConvertedRateResult(RateResult):
    currency: Currency
