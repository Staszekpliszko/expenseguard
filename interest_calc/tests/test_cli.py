"""
Testy dla CLI (main.py)
"""

from datetime import date
from pathlib import Path

import pytest
from typer.testing import CliRunner

from interest_calc.main import app

runner = CliRunner()


class TestCLIBasic:
    """Podstawowe testy CLI."""

    def test_app_help(self) -> None:
        """Test wyświetlania pomocy."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "Kalkulator odsetek" in result.stdout

    def test_calc_help(self) -> None:
        """Test wyświetlania pomocy dla komendy calc."""
        result = runner.invoke(app, ["calc", "--help"])
        assert result.exit_code == 0
        assert "principal-pln" in result.stdout
        assert "start-date" in result.stdout
        assert "rates" in result.stdout

    def test_validate_help(self) -> None:
        """Test wyświetlania pomocy dla komendy validate."""
        result = runner.invoke(app, ["validate", "--help"])
        assert result.exit_code == 0


class TestCLICalc:
    """Testy komendy calc."""

    def test_calc_missing_required_args(self) -> None:
        """Test brakujących wymaganych argumentów."""
        result = runner.invoke(app, ["calc"])
        assert result.exit_code != 0

    def test_calc_with_example_data(self, tmp_path: Path) -> None:
        """Test obliczenia z przykładowymi danymi."""
        # Użyj przykładowych danych z projektu
        rates_file = Path("interest_calc/data/rates_example.csv")

        if not rates_file.exists():
            pytest.skip("Plik rates_example.csv nie istnieje")

        result = runner.invoke(
            app,
            [
                "calc",
                "--principal-pln",
                "1000",
                "--start-date",
                "2022-01-01",
                "--end-date",
                "2022-02-01",
                "--rates",
                str(rates_file),
                "--output-dir",
                str(tmp_path),
                "--no-report",  # Nie generuj raportów w teście
            ],
        )

        # Sprawdź czy nie było błędu
        if result.exit_code != 0:
            print(f"STDOUT: {result.stdout}")
            print(f"Exit code: {result.exit_code}")

        assert result.exit_code == 0
        assert "PODSUMOWANIE" in result.stdout or "zakończone pomyślnie" in result.stdout

    def test_calc_invalid_date(self, tmp_path: Path) -> None:
        """Test nieprawidłowego formatu daty."""
        rates_file = Path("interest_calc/data/rates_example.csv")

        if not rates_file.exists():
            pytest.skip("Plik rates_example.csv nie istnieje")

        result = runner.invoke(
            app,
            [
                "calc",
                "--principal-pln",
                "1000",
                "--start-date",
                "01-01-2022",  # Zły format!
                "--rates",
                str(rates_file),
            ],
        )

        assert result.exit_code != 0
        assert "Błąd" in result.stdout or "Error" in result.stdout


class TestCLIValidate:
    """Testy komendy validate."""

    def test_validate_example_rates(self) -> None:
        """Test walidacji przykładowego pliku stawek."""
        rates_file = Path("interest_calc/data/rates_example.csv")

        if not rates_file.exists():
            pytest.skip("Plik rates_example.csv nie istnieje")

        result = runner.invoke(app, ["validate", str(rates_file)])

        # Sprawdź czy nie było błędu
        if result.exit_code != 0:
            print(f"STDOUT: {result.stdout}")

        assert result.exit_code == 0
        assert "poprawny" in result.stdout or "Wczytano" in result.stdout

    def test_validate_nonexistent_file(self) -> None:
        """Test walidacji nieistniejącego pliku."""
        result = runner.invoke(app, ["validate", "nonexistent_file.csv"])

        # Typer powinien zgłosić błąd jeśli plik nie istnieje
        assert result.exit_code != 0
