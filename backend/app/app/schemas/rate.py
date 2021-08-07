from pydantic import BaseModel, Field


class Rate(BaseModel):
    """Base Class for price components.
    Validates data type and also ensures the value is greater than 0
    """

    energy: float = Field(..., gt=0, description="The price must be greater than zero")
    time: float = Field(..., gt=0, description="The price must be greater than zero")
    transaction: float = Field(
        ..., gt=0, description="The price must be greater than zero"
    )


class CDR(BaseModel):
    """Base class for Charge Detail Record.
    Note: The only validations here are data type validation,
    complete validation is done through helper functions.(see helpers module)
    """

    timestamp_start: str = Field(
        ...,
        title="Use ISO 8601 timestamp format",
        description="The string should be a valid ISO 8601 timestamp",
    )
    timestamp_stop: str = Field(
        ...,
        title="Use ISO 8601 timestamp format",
        description="The string should be a valid ISO 8601 timestamp",
    )
    meter_start: int
    meter_stop: int


class RateResult(BaseModel):
    """Response model class for applying rate result"""

    overall: float
    components: Rate
