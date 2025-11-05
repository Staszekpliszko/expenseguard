"""
Pydantic models for interest calculation.

This module defines the core data models used throughout the application:
- RatePeriod: Represents a period with a specific interest rate
- Cashflow: Represents a single payment transaction
- Settings: Application configuration and calculation parameters
"""

from datetime import date as date_type
from enum import Enum
from pathlib import Path
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator, model_validator


class CashflowDirection(str, Enum):
    """Direction of cashflow."""

    FROM_BANK = "from_bank"
    FROM_CLIENT = "from_client"


class DayCountBasis(str, Enum):
    """Day count basis for interest calculation."""

    ACTUAL_365 = "actual/365"
    ACTUAL_360 = "actual/360"
    ACTUAL_ACTUAL = "actual/actual"


class RatePeriod(BaseModel):
    """
    Represents a period with a specific annual interest rate.

    Attributes:
        valid_from: Start date of the rate period (inclusive)
        valid_to: End date of the rate period (inclusive)
        annual_rate_percent: Annual interest rate as percentage (e.g., 10.0 for 10%)
    """

    valid_from: date_type = Field(description="Start date (inclusive)")
    valid_to: date_type = Field(description="End date (inclusive)")
    annual_rate_percent: float = Field(
        description="Annual interest rate in percent", ge=0.0, le=100.0
    )

    @model_validator(mode="after")
    def validate_date_range(self) -> "RatePeriod":
        """Ensure valid_from is before or equal to valid_to."""
        if self.valid_from > self.valid_to:
            raise ValueError(
                f"valid_from ({self.valid_from}) must be <= valid_to ({self.valid_to})"
            )
        return self

    def __lt__(self, other: "RatePeriod") -> bool:
        """Sort by valid_from date."""
        return self.valid_from < other.valid_from

    def overlaps_with(self, other: "RatePeriod") -> bool:
        """Check if this period overlaps with another period."""
        return not (self.valid_to < other.valid_from or other.valid_to < self.valid_from)


class Cashflow(BaseModel):
    """
    Represents a single cashflow transaction.

    Attributes:
        date: Transaction date
        amount_pln: Amount in PLN (positive for bank->client, negative for client->bank)
        direction: Direction of the cashflow
    """

    date: date_type = Field(description="Transaction date")
    amount_pln: float = Field(description="Amount in PLN")
    direction: CashflowDirection = Field(description="Direction of cashflow")

    @field_validator("amount_pln")
    @classmethod
    def validate_amount(cls, v: float) -> float:
        """Ensure amount is non-zero."""
        if v == 0:
            raise ValueError("amount_pln cannot be zero")
        return v

    def __lt__(self, other: "Cashflow") -> bool:
        """Sort by date."""
        return self.date < other.date


class Settings(BaseModel):
    """
    Application settings and calculation parameters.

    Attributes:
        principal_pln: Main claim amount in PLN
        principal_chf: Equivalent amount in CHF (informational only)
        fully_repaid: Whether the loan was fully repaid
        start_date: Start date for interest calculation
        end_date: End date for interest calculation
        cashflows_file: Optional path to cashflows CSV file
        rates_file: Path to interest rates CSV file
        basis: Day count basis for calculation
    """

    principal_pln: float = Field(description="Main claim amount in PLN", gt=0)
    principal_chf: Optional[float] = Field(
        default=None, description="Equivalent amount in CHF (informational)", gt=0
    )
    fully_repaid: bool = Field(default=False, description="Loan fully repaid")
    start_date: date_type = Field(description="Start date for interest calculation")
    end_date: date_type = Field(description="End date for interest calculation")
    cashflows_file: Optional[Path] = Field(
        default=None, description="Path to cashflows CSV file"
    )
    rates_file: Path = Field(description="Path to interest rates CSV file")
    basis: DayCountBasis = Field(
        default=DayCountBasis.ACTUAL_365, description="Day count basis"
    )

    @model_validator(mode="after")
    def validate_date_range(self) -> "Settings":
        """Ensure start_date is before end_date."""
        if self.start_date >= self.end_date:
            raise ValueError(
                f"start_date ({self.start_date}) must be before end_date ({self.end_date})"
            )
        return self

    @model_validator(mode="after")
    def validate_files(self) -> "Settings":
        """Ensure required files exist."""
        if not self.rates_file.exists():
            raise ValueError(f"Rates file not found: {self.rates_file}")
        if self.cashflows_file and not self.cashflows_file.exists():
            raise ValueError(f"Cashflows file not found: {self.cashflows_file}")
        return self


class InterestSegment(BaseModel):
    """
    Represents a single segment of interest calculation.

    Attributes:
        start_date: Segment start date (inclusive)
        end_date: Segment end date (exclusive)
        days: Number of days in the segment
        rate_percent: Annual interest rate for this segment
        principal: Principal amount for this segment
        interest: Calculated interest for this segment
    """

    start_date: date_type
    end_date: date_type
    days: int = Field(ge=0)
    rate_percent: float = Field(ge=0)
    principal: float
    interest: float = Field(ge=0)

    @model_validator(mode="after")
    def validate_segment(self) -> "InterestSegment":
        """Validate segment consistency."""
        if self.start_date >= self.end_date:
            raise ValueError("start_date must be before end_date")
        return self


class CalculationResult(BaseModel):
    """
    Result of interest calculation.

    Attributes:
        settings: Input settings used for calculation
        total_interest: Total calculated interest
        total_days: Total number of days
        segments: List of calculation segments
        weighted_avg_rate: Time-weighted average interest rate
    """

    settings: Settings
    total_interest: float = Field(ge=0)
    total_days: int = Field(ge=0)
    segments: list[InterestSegment]
    weighted_avg_rate: float = Field(ge=0)

    def summary_text(self) -> str:
        """Generate a summary text of the calculation."""
        lines = [
            "═" * 80,
            "STATUTORY INTEREST CALCULATION - SUMMARY",
            "═" * 80,
            f"Principal Amount (PLN):        {self.settings.principal_pln:>20,.2f}",
        ]

        if self.settings.principal_chf:
            lines.append(
                f"Principal Amount (CHF):        {self.settings.principal_chf:>20,.2f}"
            )

        lines.extend(
            [
                f"Calculation Period:            {self.settings.start_date} to {self.settings.end_date}",
                f"Total Days:                    {self.total_days:>20,}",
                f"Weighted Average Rate:         {self.weighted_avg_rate:>19.4f}%",
                f"Day Count Basis:               {self.settings.basis.value:>20}",
                "─" * 80,
                f"TOTAL INTEREST (PLN):          {self.total_interest:>20,.2f}",
                f"TOTAL CLAIM (PLN):             {self.settings.principal_pln + self.total_interest:>20,.2f}",
                "═" * 80,
                "",
                f"Number of Rate Periods:        {len(self.segments):>20,}",
                "",
                "⚠️  DISCLAIMER: This tool does not constitute legal advice.",
                "    Interest rates should be verified against official sources.",
                "    Consult with a legal professional for case-specific guidance.",
            ]
        )

        return "\n".join(lines)
