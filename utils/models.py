"""Pydantic models for data validation."""

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator


class EmergencyFundInput(BaseModel):
    """Pydantic model for validating inputs to the emergency fund calculator."""

    monthly_expenses: float = Field(
        ...,
        gt=0,
        description="""Total monthly
                                    expenses in dollars.""",
    )
    financial_obligations: float = Field(
        0.0,
        ge=0,
        description="""Additional monthly
        financial obligations (e.g., debt payments).""",
    )
    months_coverage: int = Field(
        6,
        ge=1,
        description="""Desired coverage
                                 period in months.""",
    )
    current_savings: float = Field(
        0.0,
        ge=0,
        description="""Amount already
                                   saved for emergencies.""",
    )

    @field_validator("monthly_expenses", "financial_obligations", "current_savings")
    @classmethod
    def validate_non_negative(cls, value: float) -> float:
        """Ensure that the value is non-negative."""
        if value < 0:
            error_message = "Value cannot be negative."
            raise ValueError(error_message)
        return value


class StockPriceInput(BaseModel):
    """Pydantic model for validating inputs to the stock price checker."""

    symbol: str = Field(
        ...,
        min_length=1,
        description="""Stock ticker
                        symbol (e.g., 'AAPL').""",
    )
    start_date: str | None = Field(
        None,
        description="Start date for historical data (format: 'YYYY-MM-DD').",
    )
    end_date: str | None = Field(
        None,
        description="End date for historical data (format: 'YYYY-MM-DD').",
    )


class InvestmentReturnInput(BaseModel):
    """Pydantic model for validating inputs to investment return calculator."""

    MIN_ANNUAL_RETURN = -100
    initial_amount: float = Field(
        ..., gt=0, description="Initial investment amount in dollars.",
    )
    years: float = Field(..., gt=0, description="Number of years for the investment.")
    annual_return: float = Field(
        ..., description="Annual return rate as a percentage (e.g., 5 for 5%).",
    )

    @field_validator("initial_amount")
    @classmethod
    def validate_positive_initial_amount(cls, value: float) -> float:
        """Ensure that the initial amount is positive."""
        if value <= 0:
            error_message = "Initial amount must be positive."
            raise ValueError(error_message)
        return value

    @field_validator("years")
    @classmethod
    def validate_positive_years(cls, value: float) -> float:
        """Ensure that the number of years is positive."""
        if value <= 0:
            error_message = "Years must be positive."
            raise ValueError(error_message)
        return value

    @field_validator("annual_return")
    @classmethod
    def validate_reasonable_annual_return(cls, value: float) -> float:
        """Ensure that the annual return is reasonable (not less than -100%)."""
        if value < cls.MIN_ANNUAL_RETURN:
            error_message = "Annual return cannot be less than -100%."
            raise ValueError(error_message)
        return value


class CryptoInput(BaseModel):
    """Pydantic model for validating inputs to the cryptocurrency tracker."""

    crypto_id: str = Field(
        ...,
        min_length=1,
        description="""Cryptocurrency
                           ID (e.g., 'bitcoin').""",
    )
    vs_currency: str = Field(
        default="usd",
        min_length=1,
        description="""Currency to compare
                                                    against (e.g., 'usd').""",
    )
    start_date: str | None = Field(
        None,
        description="Start date for historical data (format: 'YYYY-MM-DD').",
    )
    end_date: str | None = Field(
        None,
        description="End date for historical data (format: 'YYYY-MM-DD').",
    )

    @field_validator("start_date", "end_date")
    @classmethod
    def validate_date_format(cls, value: str | None) -> str | None:
        """Validate that the date is in the correct format (YYYY-MM-DD)."""
        if value:
            try:
                datetime.strptime(value, "%Y-%m-%d").replace(tzinfo=UTC)
            except ValueError as e:
                error_message = f"""Invalid date format: {value}.
                                    Expected format: YYYY-MM-DD."""
                raise ValueError(error_message) from e
        return value


class SpendingBreakdownInput(BaseModel):
    """Pydantic model for validating inputs to the spending breakdown tool."""

    data_source: str | None = Field(
        None,
        description=(
            "Optional path to a CSV file containing spending data. "
            "The file must have 'category' and 'amount' columns."
        ),
    )
    spending_data: dict[str, float] | None = Field(
        None,
        description="""Optional dictionary of
        spending data where keys are categories and values are amounts.""",
    )

    @field_validator("data_source", "spending_data")
    @classmethod
    def validate_inputs(
        cls,
        value: str | dict | None,
        values: dict[str, Any],
    ) -> str | dict | None:
        """Ensure that at least one of `data_source` or `spending_data` is provided.

        Args:
        ----
            value: Current field being validated.
            values: Dictionary of all previously validated fields.

        Raises:
        ------
            ValueError: If neither `data_source` nor `spending_data` is provided.

        Returns:
        -------
            The validated value.

        """
        # Check if both fields are missing
        if (
            not value
            and not values.get("data_source")
            and not values.get("spending_data")
        ):
            error_message = "Either 'data_source' or 'spending_data' must be provided."
            raise ValueError(error_message)
        return value
