"""
Testy dla modułu rates.py
"""

from datetime import date
from pathlib import Path

import pytest

from interest_calc.models import RatePeriod
from interest_calc.rates import (
    create_rate_segments,
    find_applicable_rates,
    validate_rates_no_overlap,
)


class TestRatePeriodModel:
    """Testy modelu RatePeriod."""

    def test_valid_rate_period(self) -> None:
        """Test tworzenia poprawnego okresu stawki."""
        rate = RatePeriod(
            valid_from=date(2022, 1, 1),
            valid_to=date(2022, 12, 31),
            annual_rate_percent=10.0,
        )

        assert rate.valid_from == date(2022, 1, 1)
        assert rate.valid_to == date(2022, 12, 31)
        assert rate.annual_rate_percent == 10.0

    def test_invalid_date_range(self) -> None:
        """Test walidacji: valid_from musi być przed valid_to."""
        with pytest.raises(ValueError, match="valid_from.*must be"):
            RatePeriod(
                valid_from=date(2022, 12, 31),
                valid_to=date(2022, 1, 1),  # Odwrotnie!
                annual_rate_percent=10.0,
            )

    def test_rate_out_of_range(self) -> None:
        """Test walidacji: stopa musi być w zakresie 0-100."""
        with pytest.raises(ValueError):
            RatePeriod(
                valid_from=date(2022, 1, 1),
                valid_to=date(2022, 12, 31),
                annual_rate_percent=-5.0,  # Ujemna!
            )

        with pytest.raises(ValueError):
            RatePeriod(
                valid_from=date(2022, 1, 1),
                valid_to=date(2022, 12, 31),
                annual_rate_percent=150.0,  # Ponad 100!
            )


class TestValidateRatesNoOverlap:
    """Testy walidacji nakładania się okresów."""

    def test_non_overlapping_rates(self) -> None:
        """Test dla niepokrywających się okresów."""
        rates = [
            RatePeriod(
                valid_from=date(2022, 1, 1),
                valid_to=date(2022, 6, 30),
                annual_rate_percent=10.0,
            ),
            RatePeriod(
                valid_from=date(2022, 7, 1),
                valid_to=date(2022, 12, 31),
                annual_rate_percent=12.0,
            ),
        ]

        # Nie powinno rzucić wyjątku
        validate_rates_no_overlap(rates)

    def test_overlapping_rates(self) -> None:
        """Test dla nakładających się okresów - powinien rzucić błąd."""
        rates = [
            RatePeriod(
                valid_from=date(2022, 1, 1),
                valid_to=date(2022, 7, 15),  # Pokrywa się z następnym!
                annual_rate_percent=10.0,
            ),
            RatePeriod(
                valid_from=date(2022, 7, 1),
                valid_to=date(2022, 12, 31),
                annual_rate_percent=12.0,
            ),
        ]

        with pytest.raises(ValueError, match="Nakładające się okresy"):
            validate_rates_no_overlap(rates)

    def test_adjacent_rates(self) -> None:
        """Test dla przylegających okresów (dozwolone)."""
        rates = [
            RatePeriod(
                valid_from=date(2022, 1, 1),
                valid_to=date(2022, 6, 30),
                annual_rate_percent=10.0,
            ),
            RatePeriod(
                valid_from=date(2022, 7, 1),  # Następny dzień po poprzednim
                valid_to=date(2022, 12, 31),
                annual_rate_percent=12.0,
            ),
        ]

        # Nie powinno rzucić wyjątku - przyleganie jest OK
        validate_rates_no_overlap(rates)


class TestFindApplicableRates:
    """Testy znajdowania mających zastosowanie stawek."""

    def test_find_single_applicable_rate(self) -> None:
        """Test znajdowania pojedynczej stawki pokrywającej okres."""
        rates = [
            RatePeriod(
                valid_from=date(2022, 1, 1),
                valid_to=date(2022, 12, 31),
                annual_rate_percent=10.0,
            ),
        ]

        applicable = find_applicable_rates(
            rates, start_date=date(2022, 6, 1), end_date=date(2022, 7, 1)
        )

        assert len(applicable) == 1
        assert applicable[0].annual_rate_percent == 10.0

    def test_find_multiple_applicable_rates(self) -> None:
        """Test znajdowania wielu stawek pokrywających okres."""
        rates = [
            RatePeriod(
                valid_from=date(2022, 1, 1),
                valid_to=date(2022, 6, 30),
                annual_rate_percent=10.0,
            ),
            RatePeriod(
                valid_from=date(2022, 7, 1),
                valid_to=date(2022, 12, 31),
                annual_rate_percent=12.0,
            ),
        ]

        # Okres przechodzący przez obie stawki
        applicable = find_applicable_rates(
            rates, start_date=date(2022, 5, 1), end_date=date(2022, 8, 1)
        )

        assert len(applicable) == 2

    def test_no_applicable_rates(self) -> None:
        """Test gdy brak stawek pokrywających okres - powinien rzucić błąd."""
        rates = [
            RatePeriod(
                valid_from=date(2022, 1, 1),
                valid_to=date(2022, 12, 31),
                annual_rate_percent=10.0,
            ),
        ]

        # Okres poza zakresem stawek
        with pytest.raises(ValueError, match="Brak stawek odsetek pokrywających okres"):
            find_applicable_rates(
                rates, start_date=date(2023, 1, 1), end_date=date(2023, 2, 1)
            )


class TestCreateRateSegments:
    """Testy tworzenia segmentów stawek."""

    def test_create_segments_single_rate(self) -> None:
        """Test tworzenia segmentów dla pojedynczej stawki."""
        rates = [
            RatePeriod(
                valid_from=date(2022, 1, 1),
                valid_to=date(2022, 12, 31),
                annual_rate_percent=10.0,
            ),
        ]

        segments = create_rate_segments(
            rates, start_date=date(2022, 6, 1), end_date=date(2022, 7, 1)
        )

        assert len(segments) == 1
        seg_start, seg_end, rate = segments[0]
        assert seg_start == date(2022, 6, 1)
        assert seg_end == date(2022, 7, 1)
        assert rate == 10.0

    def test_create_segments_multiple_rates(self) -> None:
        """Test tworzenia segmentów dla wielu stawek."""
        rates = [
            RatePeriod(
                valid_from=date(2022, 1, 1),
                valid_to=date(2022, 6, 30),
                annual_rate_percent=10.0,
            ),
            RatePeriod(
                valid_from=date(2022, 7, 1),
                valid_to=date(2022, 12, 31),
                annual_rate_percent=12.0,
            ),
        ]

        # Okres obejmujący obie stawki
        segments = create_rate_segments(
            rates, start_date=date(2022, 6, 15), end_date=date(2022, 7, 15)
        )

        assert len(segments) == 2

        # Pierwszy segment: 2022-06-15 do 2022-07-01 (koniec pierwszej stawki + 1 dzień)
        seg1_start, seg1_end, rate1 = segments[0]
        assert seg1_start == date(2022, 6, 15)
        assert seg1_end == date(2022, 7, 1)
        assert rate1 == 10.0

        # Drugi segment: 2022-07-01 do 2022-07-15
        seg2_start, seg2_end, rate2 = segments[1]
        assert seg2_start == date(2022, 7, 1)
        assert seg2_end == date(2022, 7, 15)
        assert rate2 == 12.0

    def test_create_segments_incomplete_coverage(self) -> None:
        """Test gdy stawki nie pokrywają całego okresu - powinien rzucić błąd."""
        rates = [
            RatePeriod(
                valid_from=date(2022, 1, 1),
                valid_to=date(2022, 6, 30),
                annual_rate_percent=10.0,
            ),
            # Luka: brak stawki dla lipca!
            RatePeriod(
                valid_from=date(2022, 8, 1),
                valid_to=date(2022, 12, 31),
                annual_rate_percent=12.0,
            ),
        ]

        # Próba obliczenia dla okresu z luką
        with pytest.raises(ValueError, match="nie pokrywają całego okresu"):
            create_rate_segments(
                rates, start_date=date(2022, 6, 1), end_date=date(2022, 8, 15)
            )
