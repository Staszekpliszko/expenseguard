"""
Moduł narzędziowy z funkcjami pomocniczymi.

Zawiera funkcje do:
- Parsowania dat
- Obliczania liczby dni między datami (day count)
- Walidacji okresów
"""

from datetime import date, datetime
from typing import Union

from interest_calc.models import DayCountBasis


def parse_date(date_str: str) -> date:
    """
    Parsuje string daty w formacie YYYY-MM-DD do obiektu date.

    Args:
        date_str: String daty w formacie YYYY-MM-DD

    Returns:
        Obiekt date

    Raises:
        ValueError: Jeśli format daty jest nieprawidłowy
    """
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError as e:
        raise ValueError(f"Nieprawidłowy format daty '{date_str}'. Użyj YYYY-MM-DD.") from e


def days_between(
    start: date, end: date, basis: DayCountBasis = DayCountBasis.ACTUAL_365
) -> int:
    """
    Oblicza liczbę dni między dwiema datami (włącznie z datą początkową, bez końcowej).

    Standardowa konwencja: [start, end) - "from inclusive, to exclusive"

    Args:
        start: Data początkowa (włączona)
        end: Data końcowa (wyłączona)
        basis: Sposób liczenia dni (domyślnie actual/365)

    Returns:
        Liczba dni

    Raises:
        ValueError: Jeśli start >= end
    """
    if start >= end:
        raise ValueError(f"Data początkowa ({start}) musi być przed datą końcową ({end})")

    delta = end - start
    return delta.days


def day_count_factor(
    start: date, end: date, basis: DayCountBasis = DayCountBasis.ACTUAL_365
) -> float:
    """
    Oblicza współczynnik frakcji roku dla danego okresu.

    Args:
        start: Data początkowa
        end: Data końcowa
        basis: Sposób liczenia dni

    Returns:
        Współczynnik (np. 0.5 dla pół roku przy actual/365)
    """
    days = days_between(start, end, basis)

    if basis == DayCountBasis.ACTUAL_365:
        return days / 365.0
    elif basis == DayCountBasis.ACTUAL_360:
        return days / 360.0
    elif basis == DayCountBasis.ACTUAL_ACTUAL:
        # Dla actual/actual liczymy faktyczne dni w roku
        # Dla uproszczenia używamy 365.25 (uwzględnia lata przestępne)
        return days / 365.25
    else:
        raise ValueError(f"Nieobsługiwany basis: {basis}")


def validate_no_gaps(periods: list[tuple[date, date]]) -> None:
    """
    Waliduje, że lista okresów nie ma luk czasowych.

    Args:
        periods: Lista krotek (start_date, end_date)

    Raises:
        ValueError: Jeśli znaleziono lukę między okresami
    """
    if not periods:
        return

    sorted_periods = sorted(periods, key=lambda x: x[0])

    for i in range(len(sorted_periods) - 1):
        current_end = sorted_periods[i][1]
        next_start = sorted_periods[i + 1][0]

        # Koniec bieżącego okresu powinien być równy lub następować bezpośrednio przed początkiem następnego
        if current_end < next_start:
            raise ValueError(
                f"Luka między okresami: {current_end} -> {next_start}. "
                f"Okresy stawek muszą pokrywać cały zakres bez luk."
            )


def validate_no_overlaps(periods: list[tuple[date, date]]) -> None:
    """
    Waliduje, że lista okresów nie ma nakładających się zakresów.

    Args:
        periods: Lista krotek (start_date, end_date)

    Raises:
        ValueError: Jeśli okresy się nakładają
    """
    if not periods:
        return

    sorted_periods = sorted(periods, key=lambda x: x[0])

    for i in range(len(sorted_periods) - 1):
        current_end = sorted_periods[i][1]
        next_start = sorted_periods[i + 1][0]

        # Okresy się nakładają jeśli koniec bieżącego jest po początku następnego
        # Dozwolone jest current_end == next_start (bezpośrednie przyleganie)
        if current_end > next_start:
            raise ValueError(
                f"Nakładające się okresy: "
                f"[{sorted_periods[i][0]} - {current_end}] i "
                f"[{next_start} - {sorted_periods[i + 1][1]}]"
            )


def format_currency(amount: float, currency: str = "PLN") -> str:
    """
    Formatuje kwotę jako walutę z odpowiednim separatorem tysięcy.

    Args:
        amount: Kwota do sformatowania
        currency: Symbol waluty

    Returns:
        Sformatowany string (np. "112,000.00 PLN")
    """
    return f"{amount:,.2f} {currency}"


def format_percentage(rate: float) -> str:
    """
    Formatuje stopę procentową.

    Args:
        rate: Stopa procentowa (np. 10.5)

    Returns:
        Sformatowany string (np. "10.50%")
    """
    return f"{rate:.2f}%"
