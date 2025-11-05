"""
Silnik obliczania odsetek ustawowych za opóźnienie (Art. 481 KC).

Główna logika aplikacji:
- Obliczanie odsetek piecewise przez różne okresy stawek
- Obsługa wielu podstaw do naliczania (cashflows)
- Brak kapitalizacji odsetek
"""

import csv
from datetime import date
from pathlib import Path
from typing import Optional

from interest_calc.models import (
    CalculationResult,
    Cashflow,
    CashflowDirection,
    InterestSegment,
    RatePeriod,
    Settings,
)
from interest_calc.rates import create_rate_segments, load_rates_from_csv
from interest_calc.utils import days_between, parse_date


def load_cashflows_from_csv(file_path: Path) -> list[Cashflow]:
    """
    Wczytuje przepływy pieniężne z pliku CSV.

    Format CSV:
    date,amount_pln,direction
    2005-06-01,112000,from_bank
    2005-07-10,-1200,from_client

    Args:
        file_path: Ścieżka do pliku CSV z przepływami

    Returns:
        Lista posortowanych Cashflow

    Raises:
        FileNotFoundError: Jeśli plik nie istnieje
        ValueError: Jeśli format pliku jest nieprawidłowy
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Plik z przepływami nie został znaleziony: {file_path}")

    cashflows: list[Cashflow] = []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            # Filtruj linie zaczynające się od # (komentarze)
            lines = [line for line in f if not line.strip().startswith("#")]
            reader = csv.DictReader(lines)

            # Walidacja nagłówków
            required_columns = {"date", "amount_pln", "direction"}
            if not required_columns.issubset(set(reader.fieldnames or [])):
                raise ValueError(
                    f"Plik CSV musi zawierać kolumny: {required_columns}. "
                    f"Znaleziono: {reader.fieldnames}"
                )

            for row_num, row in enumerate(reader, start=2):
                try:
                    cashflow = Cashflow(
                        date=parse_date(row["date"].strip()),
                        amount_pln=float(row["amount_pln"].strip()),
                        direction=CashflowDirection(row["direction"].strip()),
                    )
                    cashflows.append(cashflow)
                except (ValueError, KeyError) as e:
                    raise ValueError(
                        f"Błąd w wierszu {row_num} pliku {file_path}: {e}"
                    ) from e

    except Exception as e:
        if isinstance(e, ValueError):
            raise
        raise ValueError(f"Nie można wczytać pliku {file_path}: {e}") from e

    if not cashflows:
        raise ValueError(f"Plik {file_path} nie zawiera żadnych przepływów pieniężnych")

    # Sortuj według daty
    cashflows.sort()

    return cashflows


def calculate_interest_for_principal(
    principal: float,
    start_date: date,
    end_date: date,
    rate_segments: list[tuple[date, date, float]],
    basis_days_per_year: int = 365,
) -> tuple[float, list[InterestSegment]]:
    """
    Oblicza odsetki dla pojedynczej kwoty głównej przez wszystkie segmenty stawek.

    Wzór: interest = principal * (rate/100) * (days/days_per_year)

    Args:
        principal: Kwota główna do oprocentowania
        start_date: Data początkowa naliczania
        end_date: Data końcowa naliczania
        rate_segments: Lista segmentów (seg_start, seg_end, rate_percent)
        basis_days_per_year: Liczba dni w roku dla obliczeń (domyślnie 365)

    Returns:
        Tuple (łączne odsetki, lista segmentów)
    """
    total_interest = 0.0
    segments: list[InterestSegment] = []

    for seg_start, seg_end, rate_percent in rate_segments:
        # Ogranicz segment do naszego okresu naliczania
        effective_start = max(seg_start, start_date)
        effective_end = min(seg_end, end_date)

        # Jeśli segment ma sens
        if effective_start < effective_end:
            days = days_between(effective_start, effective_end)

            # Oblicz odsetki: principal * (rate/100) * (days/days_per_year)
            interest = principal * (rate_percent / 100.0) * (days / basis_days_per_year)

            segment = InterestSegment(
                start_date=effective_start,
                end_date=effective_end,
                days=days,
                rate_percent=rate_percent,
                principal=principal,
                interest=interest,
            )

            segments.append(segment)
            total_interest += interest

    return total_interest, segments


def calculate_interest(settings: Settings) -> CalculationResult:
    """
    Główna funkcja obliczająca odsetki ustawowe za opóźnienie.

    Algorytm:
    1. Wczytaj stawki odsetek z pliku
    2. Wczytaj przepływy (jeśli podane)
    3. Utwórz segmenty stawek dla okresu [start_date, end_date)
    4. Dla każdej podstawy (principal lub każdy cashflow) oblicz odsetki
    5. Zsumuj wyniki

    Args:
        settings: Ustawienia obliczeń

    Returns:
        CalculationResult z pełnymi wynikami obliczeń

    Raises:
        ValueError: Jeśli dane są niespójne lub niepełne
    """
    # Wczytaj stawki odsetek
    rates = load_rates_from_csv(settings.rates_file)

    # Utwórz segmenty stawek dla okresu naliczania
    rate_segments = create_rate_segments(rates, settings.start_date, settings.end_date)

    # Określ basis (dni w roku)
    if settings.basis.value == "actual/365":
        basis_days = 365
    elif settings.basis.value == "actual/360":
        basis_days = 360
    else:  # actual/actual
        basis_days = 365  # Używamy 365 jako przybliżenie

    all_segments: list[InterestSegment] = []
    total_interest = 0.0

    # Jeśli są cashflows, oblicz odsetki dla każdego przepływu
    if settings.cashflows_file:
        cashflows = load_cashflows_from_csv(settings.cashflows_file)

        for cashflow in cashflows:
            # Dla cashflows z kierunkiem from_bank (dodatnie) naliczamy odsetki
            # Dla from_client (ujemne) też możemy naliczyć, jeśli kwota jest ujemna
            # Na razie traktujemy wartość bezwzględną amount_pln jako podstawę

            # Sprawdź czy cashflow jest w okresie naliczania
            if cashflow.date >= settings.end_date:
                continue  # Cashflow po okresie naliczania - pomijamy

            # Ustal datę początkową naliczania dla tego cashflow
            # Jeśli cashflow jest przed start_date, liczymy od start_date
            # Jeśli cashflow jest po start_date, liczymy od daty cashflow
            cf_start = max(cashflow.date, settings.start_date)

            # Tylko jeśli cf_start < end_date (jest co liczyć)
            if cf_start < settings.end_date:
                # Użyj wartości bezwzględnej jako podstawy
                principal = abs(cashflow.amount_pln)

                interest, segments = calculate_interest_for_principal(
                    principal=principal,
                    start_date=cf_start,
                    end_date=settings.end_date,
                    rate_segments=rate_segments,
                    basis_days_per_year=basis_days,
                )

                total_interest += interest
                all_segments.extend(segments)

    else:
        # Brak cashflows - licz odsetki od samej kwoty głównej
        interest, segments = calculate_interest_for_principal(
            principal=settings.principal_pln,
            start_date=settings.start_date,
            end_date=settings.end_date,
            rate_segments=rate_segments,
            basis_days_per_year=basis_days,
        )

        total_interest = interest
        all_segments = segments

    # Oblicz łączną liczbę dni i średnią ważoną stopę
    total_days = days_between(settings.start_date, settings.end_date)

    # Średnia ważona stopa = suma(rate * days) / total_days
    if total_days > 0 and all_segments:
        weighted_sum = sum(seg.rate_percent * seg.days for seg in all_segments)
        # Dzielimy przez sumę dni z segmentów (które mogą być różne dla różnych cashflows)
        total_segment_days = sum(seg.days for seg in all_segments)
        weighted_avg_rate = weighted_sum / total_segment_days if total_segment_days > 0 else 0.0
    else:
        weighted_avg_rate = 0.0

    return CalculationResult(
        settings=settings,
        total_interest=total_interest,
        total_days=total_days,
        segments=all_segments,
        weighted_avg_rate=weighted_avg_rate,
    )


def calculate_simple_interest(
    principal: float,
    annual_rate_percent: float,
    days: int,
    basis_days_per_year: int = 365,
) -> float:
    """
    Prosta funkcja pomocnicza do obliczania odsetek prostych.

    Wzór: interest = principal * (rate/100) * (days/basis)

    Args:
        principal: Kwota główna
        annual_rate_percent: Roczna stopa procentowa
        days: Liczba dni
        basis_days_per_year: Liczba dni w roku (domyślnie 365)

    Returns:
        Obliczone odsetki
    """
    return principal * (annual_rate_percent / 100.0) * (days / basis_days_per_year)
