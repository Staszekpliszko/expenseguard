"""
Testy dla modułu engine.py
"""

from datetime import date
from pathlib import Path

import pytest

from interest_calc.engine import (
    calculate_interest_for_principal,
    calculate_simple_interest,
)
from interest_calc.models import DayCountBasis, Settings


class TestSimpleInterest:
    """Testy funkcji calculate_simple_interest."""

    def test_simple_interest_calculation(self) -> None:
        """Test prostego obliczenia odsetek: 1000 PLN, 10%, 30 dni."""
        # 1000 PLN przez 30 dni przy 10% rocznie
        # Oczekiwane: 1000 * 0.10 * (30/365) = 8.219...
        result = calculate_simple_interest(
            principal=1000.0, annual_rate_percent=10.0, days=30, basis_days_per_year=365
        )

        expected = 1000.0 * 0.10 * (30 / 365)
        assert abs(result - expected) < 0.01

    def test_simple_interest_full_year(self) -> None:
        """Test odsetek za pełny rok: 10000 PLN, 5%, 365 dni."""
        result = calculate_simple_interest(
            principal=10000.0, annual_rate_percent=5.0, days=365, basis_days_per_year=365
        )

        # Za pełny rok powinno być dokładnie 5% z 10000 = 500
        assert abs(result - 500.0) < 0.01

    def test_simple_interest_zero_days(self) -> None:
        """Test odsetek dla 0 dni - powinny być 0."""
        result = calculate_simple_interest(
            principal=1000.0, annual_rate_percent=10.0, days=0, basis_days_per_year=365
        )

        assert result == 0.0


class TestInterestForPrincipal:
    """Testy funkcji calculate_interest_for_principal."""

    def test_single_rate_period(self) -> None:
        """Test obliczenia dla pojedynczego okresu stawki."""
        # 1000 PLN od 2022-01-01 do 2022-01-31 (30 dni) przy 10%
        rate_segments = [(date(2022, 1, 1), date(2022, 1, 31), 10.0)]

        total_interest, segments = calculate_interest_for_principal(
            principal=1000.0,
            start_date=date(2022, 1, 1),
            end_date=date(2022, 1, 31),
            rate_segments=rate_segments,
            basis_days_per_year=365,
        )

        # Oczekiwane: 1000 * 0.10 * (30/365) ≈ 8.22
        expected = 1000.0 * 0.10 * (30 / 365)
        assert abs(total_interest - expected) < 0.01
        assert len(segments) == 1
        assert segments[0].days == 30
        assert segments[0].rate_percent == 10.0

    def test_two_rate_periods(self) -> None:
        """Test obliczenia dla dwóch okresów ze zmianą stawki w połowie."""
        # 1000 PLN od 2022-01-01 do 2022-02-01 (31 dni)
        # Zmiana stawki w połowie: 2022-01-16
        # Pierwszy okres: 2022-01-01 do 2022-01-16 (15 dni) przy 10%
        # Drugi okres: 2022-01-16 do 2022-02-01 (16 dni) przy 12%

        rate_segments = [
            (date(2022, 1, 1), date(2022, 1, 16), 10.0),
            (date(2022, 1, 16), date(2022, 2, 1), 12.0),
        ]

        total_interest, segments = calculate_interest_for_principal(
            principal=1000.0,
            start_date=date(2022, 1, 1),
            end_date=date(2022, 2, 1),
            rate_segments=rate_segments,
            basis_days_per_year=365,
        )

        # Okres 1: 1000 * 0.10 * (15/365) ≈ 4.11
        # Okres 2: 1000 * 0.12 * (16/365) ≈ 5.26
        # Suma: ≈ 9.37
        expected1 = 1000.0 * 0.10 * (15 / 365)
        expected2 = 1000.0 * 0.12 * (16 / 365)
        expected_total = expected1 + expected2

        assert abs(total_interest - expected_total) < 0.01
        assert len(segments) == 2

    def test_partial_overlap(self) -> None:
        """Test gdy okres naliczania pokrywa tylko część segmentów stawek."""
        # Segmenty pokrywają cały 2022, ale liczymy tylko styczeń
        rate_segments = [
            (date(2022, 1, 1), date(2022, 6, 30), 10.0),
            (date(2022, 7, 1), date(2022, 12, 31), 12.0),
        ]

        total_interest, segments = calculate_interest_for_principal(
            principal=1000.0,
            start_date=date(2022, 1, 1),
            end_date=date(2022, 2, 1),  # Tylko styczeń
            rate_segments=rate_segments,
            basis_days_per_year=365,
        )

        # Powinien użyć tylko pierwszego segmentu (10%), 31 dni
        expected = 1000.0 * 0.10 * (31 / 365)
        assert abs(total_interest - expected) < 0.01
        assert len(segments) == 1
        assert segments[0].rate_percent == 10.0
        assert segments[0].days == 31
