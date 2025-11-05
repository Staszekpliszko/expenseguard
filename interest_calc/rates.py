"""
Moduł do wczytywania i walidacji stawek odsetek ustawowych.

Obsługuje:
- Wczytywanie stawek z pliku CSV
- Walidację okresów (brak nakładania, pokrycie całego zakresu)
- Sortowanie i przygotowanie danych do obliczeń
"""

import csv
from datetime import date
from pathlib import Path
from typing import Optional

from interest_calc.models import RatePeriod
from interest_calc.utils import parse_date, validate_no_overlaps


def load_rates_from_csv(file_path: Path) -> list[RatePeriod]:
    """
    Wczytuje stawki odsetek z pliku CSV.

    Format CSV:
    valid_from,valid_to,annual_rate_percent
    2022-01-01,2022-06-30,10.0
    2022-07-01,2022-12-31,12.0

    Args:
        file_path: Ścieżka do pliku CSV ze stawkami

    Returns:
        Lista posortowanych RatePeriod

    Raises:
        FileNotFoundError: Jeśli plik nie istnieje
        ValueError: Jeśli format pliku jest nieprawidłowy lub dane są niespójne
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Plik ze stawkami nie został znaleziony: {file_path}")

    rates: list[RatePeriod] = []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            # Filtruj linie zaczynające się od # (komentarze)
            lines = [line for line in f if not line.strip().startswith("#")]
            reader = csv.DictReader(lines)

            # Walidacja nagłówków
            required_columns = {"valid_from", "valid_to", "annual_rate_percent"}
            if not required_columns.issubset(set(reader.fieldnames or [])):
                raise ValueError(
                    f"Plik CSV musi zawierać kolumny: {required_columns}. "
                    f"Znaleziono: {reader.fieldnames}"
                )

            for row_num, row in enumerate(reader, start=2):  # Start at 2 (1 is header)
                try:
                    rate = RatePeriod(
                        valid_from=parse_date(row["valid_from"].strip()),
                        valid_to=parse_date(row["valid_to"].strip()),
                        annual_rate_percent=float(row["annual_rate_percent"].strip()),
                    )
                    rates.append(rate)
                except (ValueError, KeyError) as e:
                    raise ValueError(
                        f"Błąd w wierszu {row_num} pliku {file_path}: {e}"
                    ) from e

    except Exception as e:
        if isinstance(e, ValueError):
            raise
        raise ValueError(f"Nie można wczytać pliku {file_path}: {e}") from e

    if not rates:
        raise ValueError(f"Plik {file_path} nie zawiera żadnych stawek odsetek")

    # Sortuj według daty początkowej
    rates.sort()

    # Waliduj brak nakładania się okresów
    validate_rates_no_overlap(rates)

    return rates


def validate_rates_no_overlap(rates: list[RatePeriod]) -> None:
    """
    Sprawdza, czy okresy stawek nie nakładają się na siebie.

    Args:
        rates: Lista okresów stawek

    Raises:
        ValueError: Jeśli okresy się nakładają
    """
    periods = [(r.valid_from, r.valid_to) for r in rates]
    validate_no_overlaps(periods)


def find_applicable_rates(
    rates: list[RatePeriod], start_date: date, end_date: date
) -> list[RatePeriod]:
    """
    Znajduje stawki mające zastosowanie w danym okresie [start_date, end_date).

    Args:
        rates: Lista wszystkich dostępnych stawek (posortowana)
        start_date: Data początkowa (włączona)
        end_date: Data końcowa (wyłączona)

    Returns:
        Lista stawek, które pokrywają lub przecinają się z zadanym okresem

    Raises:
        ValueError: Jeśli brak stawek pokrywających żądany okres
    """
    if start_date >= end_date:
        raise ValueError(f"start_date ({start_date}) musi być przed end_date ({end_date})")

    applicable: list[RatePeriod] = []

    # Ważna data końcowa dla sprawdzenia jest faktycznie end_date - 1 dzień,
    # bo end_date jest wyłączona z obliczeń
    effective_end = end_date

    for rate in rates:
        # Sprawdź czy okres stawki przecina się z [start_date, end_date)
        # Okres stawki to [valid_from, valid_to] (oba włączone)
        # Nasz okres to [start_date, end_date) (start włączony, end wyłączony)

        # Okresy się nie przecinają jeśli:
        # - stawka kończy się przed naszym startem: rate.valid_to < start_date
        # - stawka zaczyna się w lub po naszym końcu: rate.valid_from >= end_date

        if rate.valid_to < start_date:
            continue
        if rate.valid_from >= effective_end:
            continue

        applicable.append(rate)

    if not applicable:
        raise ValueError(
            f"Brak stawek odsetek pokrywających okres od {start_date} do {end_date}. "
            f"Zaktualizuj plik ze stawkami."
        )

    return applicable


def create_rate_segments(
    rates: list[RatePeriod], start_date: date, end_date: date
) -> list[tuple[date, date, float]]:
    """
    Tworzy segmenty [seg_start, seg_end) z odpowiednimi stawkami dla danego okresu.

    Każdy segment pokrywa część okresu [start_date, end_date) z jedną stawką.
    Segmenty są przylegające i pokrywają cały okres bez luk.

    Args:
        rates: Lista stawek odsetek (posortowana)
        start_date: Data początkowa okresu naliczania (włączona)
        end_date: Data końcowa okresu naliczania (wyłączona)

    Returns:
        Lista krotek (segment_start, segment_end, rate_percent)
        gdzie segment_start jest włączone, a segment_end wyłączone

    Raises:
        ValueError: Jeśli stawki nie pokrywają całego okresu
    """
    applicable = find_applicable_rates(rates, start_date, end_date)

    segments: list[tuple[date, date, float]] = []
    current_date = start_date

    for rate in applicable:
        # Początek segmentu to max(current_date, rate.valid_from)
        seg_start = max(current_date, rate.valid_from)

        # Koniec segmentu to min(end_date, rate.valid_to + 1 dzień)
        # rate.valid_to jest włączone, więc dodajemy 1 dzień dla wyłączenia
        from datetime import timedelta

        rate_end_exclusive = rate.valid_to + timedelta(days=1)
        seg_end = min(end_date, rate_end_exclusive)

        # Jeśli segment ma senS (start < end), dodaj go
        if seg_start < seg_end:
            segments.append((seg_start, seg_end, rate.annual_rate_percent))
            current_date = seg_end

        # Jeśli dotarliśmy do końca żądanego okresu, kończymy
        if current_date >= end_date:
            break

    # Sprawdź czy cały okres jest pokryty
    if current_date < end_date:
        raise ValueError(
            f"Stawki nie pokrywają całego okresu. Pokryto do {current_date}, "
            f"ale żądany koniec to {end_date}. Zaktualizuj plik ze stawkami."
        )

    return segments


def save_rates_to_csv(rates: list[RatePeriod], file_path: Path) -> None:
    """
    Zapisuje stawki odsetek do pliku CSV.

    Args:
        rates: Lista okresów stawek
        file_path: Ścieżka do pliku CSV

    Raises:
        IOError: Jeśli nie można zapisać pliku
    """
    try:
        with open(file_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(
                f, fieldnames=["valid_from", "valid_to", "annual_rate_percent"]
            )
            writer.writeheader()

            for rate in sorted(rates):
                writer.writerow(
                    {
                        "valid_from": rate.valid_from.isoformat(),
                        "valid_to": rate.valid_to.isoformat(),
                        "annual_rate_percent": rate.annual_rate_percent,
                    }
                )
    except Exception as e:
        raise IOError(f"Nie można zapisać pliku {file_path}: {e}") from e
