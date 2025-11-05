"""
Interfejs CLI dla kalkulatora odsetek ustawowych za opóźnienie.

Główna komenda: calc
Używa biblioteki Typer do obsługi argumentów i opcji wiersza poleceń.
"""

from datetime import date
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from interest_calc.engine import calculate_interest
from interest_calc.models import DayCountBasis, Settings
from interest_calc.report import save_reports

app = typer.Typer(
    name="interest-calc",
    help="Kalkulator odsetek ustawowych za opóźnienie (Art. 481 KC) dla spraw frankowych",
    add_completion=False,
)

console = Console()


def version_callback(value: bool) -> None:
    """Callback dla opcji --version."""
    if value:
        from interest_calc import __version__

        console.print(f"interest-calc v{__version__}")
        raise typer.Exit()


@app.command(name="calc")
def calculate(
    principal_pln: float = typer.Option(
        ...,
        "--principal-pln",
        help="Główna kwota roszczenia w PLN (np. 112000)",
        min=0.01,
    ),
    principal_chf: Optional[float] = typer.Option(
        None,
        "--principal-chf",
        help="Równoważna kwota w CHF (opcjonalnie, tylko informacyjnie)",
        min=0.01,
    ),
    fully_repaid: bool = typer.Option(
        False,
        "--fully-repaid",
        help="Czy kredyt został spłacony w 100%",
    ),
    start_date: str = typer.Option(
        ...,
        "--start-date",
        help="Data początku opóźnienia w formacie YYYY-MM-DD (np. data doręczenia pozwu)",
    ),
    end_date: Optional[str] = typer.Option(
        None,
        "--end-date",
        help="Data końca naliczania w formacie YYYY-MM-DD (domyślnie dzisiaj)",
    ),
    cashflows: Optional[Path] = typer.Option(
        None,
        "--cashflows",
        help="Ścieżka do pliku CSV z przepływami pieniężnymi",
        exists=True,
        file_okay=True,
        dir_okay=False,
    ),
    rates: Path = typer.Option(
        ...,
        "--rates",
        help="Ścieżka do pliku CSV ze stawkami odsetek",
        exists=True,
        file_okay=True,
        dir_okay=False,
    ),
    basis: DayCountBasis = typer.Option(
        DayCountBasis.ACTUAL_365,
        "--basis",
        help="Zasady bazowe liczenia dni",
    ),
    output_dir: Path = typer.Option(
        Path("reports"),
        "--output-dir",
        help="Katalog wyjściowy dla raportów",
    ),
    no_report: bool = typer.Option(
        False,
        "--no-report",
        help="Nie generuj raportów CSV/XLSX, tylko wyświetl wynik w terminalu",
    ),
) -> None:
    """
    Oblicza odsetki ustawowe za opóźnienie (Art. 481 KC) dla spraw frankowych.

    Przykłady użycia:

    \b
    # Podstawowe obliczenie dla kwoty głównej:
    interest-calc calc \\
        --principal-pln 112000 \\
        --start-date 2022-05-10 \\
        --rates data/rates_example.csv

    \b
    # Z przepływami pieniężnymi i równoważną kwotą CHF:
    interest-calc calc \\
        --principal-pln 112000 \\
        --principal-chf 47000 \\
        --start-date 2022-05-10 \\
        --end-date 2023-05-10 \\
        --cashflows data/cashflows_example.csv \\
        --rates data/rates_example.csv \\
        --fully-repaid

    \b
    # Zmiana katalogu wyjściowego i basis:
    interest-calc calc \\
        --principal-pln 112000 \\
        --start-date 2022-05-10 \\
        --rates data/rates_example.csv \\
        --basis actual/360 \\
        --output-dir ./my_reports
    """
    try:
        # Parsuj daty
        from interest_calc.utils import parse_date

        start_dt = parse_date(start_date)
        end_dt = parse_date(end_date) if end_date else date.today()

        # Waliduj daty
        if start_dt >= end_dt:
            console.print(
                f"[red]Błąd:[/red] Data początkowa ({start_dt}) "
                f"musi być przed datą końcową ({end_dt})",
                style="bold red",
            )
            raise typer.Exit(code=1)

        # Wyświetl informacje o rozpoczęciu obliczeń
        console.print("\n[bold blue]🔢 Rozpoczynam obliczanie odsetek...[/bold blue]\n")

        # Utwórz settings
        settings = Settings(
            principal_pln=principal_pln,
            principal_chf=principal_chf,
            fully_repaid=fully_repaid,
            start_date=start_dt,
            end_date=end_dt,
            cashflows_file=cashflows,
            rates_file=rates,
            basis=basis,
        )

        # Oblicz odsetki
        result = calculate_interest(settings)

        # Wyświetl wyniki w terminalu
        display_results(result)

        # Zapisz raporty (jeśli nie --no-report)
        if not no_report:
            console.print("\n[bold blue]📊 Generuję raporty...[/bold blue]\n")
            csv_path, xlsx_path = save_reports(result, output_dir)

            console.print(f"[green]✓[/green] Raport CSV zapisany: {csv_path}")
            console.print(f"[green]✓[/green] Raport XLSX zapisany: {xlsx_path}")

        console.print(
            "\n[bold green]✓ Obliczenia zakończone pomyślnie![/bold green]\n",
        )

    except ValueError as e:
        console.print(f"\n[bold red]Błąd:[/bold red] {e}\n", style="red")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(
            f"\n[bold red]Nieoczekiwany błąd:[/bold red] {e}\n", style="red"
        )
        raise typer.Exit(code=1)


def display_results(result) -> None:
    """
    Wyświetla wyniki obliczeń w terminalu z formatowaniem Rich.

    Args:
        result: CalculationResult do wyświetlenia
    """
    from interest_calc.models import CalculationResult

    # Panel z podsumowaniem
    summary_text = f"""
[bold]Kwota główna (PLN):[/bold]        {result.settings.principal_pln:>20,.2f}
"""

    if result.settings.principal_chf:
        summary_text += f"""[bold]Kwota główna (CHF):[/bold]        {result.settings.principal_chf:>20,.2f}
"""

    summary_text += f"""[bold]Okres obliczeń:[/bold]            {result.settings.start_date} do {result.settings.end_date}
[bold]Liczba dni:[/bold]                {result.total_days:>20,}
[bold]Średnia ważona stopa:[/bold]      {result.weighted_avg_rate:>19.4f}%
[bold]Podstawa liczenia:[/bold]         {result.settings.basis.value:>20}

[bold yellow]ŁĄCZNE ODSETKI (PLN):[/bold yellow]     {result.total_interest:>20,.2f}
[bold cyan]ŁĄCZNE ROSZCZENIE (PLN):[/bold cyan]   {result.settings.principal_pln + result.total_interest:>20,.2f}
"""

    console.print(
        Panel(
            summary_text,
            title="[bold]PODSUMOWANIE OBLICZEŃ[/bold]",
            border_style="blue",
            expand=False,
        )
    )

    # Tabela z segmentami
    if result.segments:
        console.print(f"\n[bold]Szczegółowe segmenty ({len(result.segments)} okresów):[/bold]\n")

        table = Table(show_header=True, header_style="bold magenta", show_lines=True)
        table.add_column("Data od", style="cyan", justify="center")
        table.add_column("Data do", style="cyan", justify="center")
        table.add_column("Dni", justify="right")
        table.add_column("Stopa (%)", justify="right")
        table.add_column("Podstawa (PLN)", justify="right")
        table.add_column("Odsetki (PLN)", justify="right", style="yellow")

        total_interest_check = 0.0

        for segment in result.segments:
            table.add_row(
                str(segment.start_date),
                str(segment.end_date),
                f"{segment.days:,}",
                f"{segment.rate_percent:.2f}",
                f"{segment.principal:,.2f}",
                f"{segment.interest:,.2f}",
            )
            total_interest_check += segment.interest

        # Wiersz z sumą
        table.add_row(
            "[bold]SUMA[/bold]",
            "",
            f"[bold]{sum(s.days for s in result.segments):,}[/bold]",
            "",
            "",
            f"[bold]{total_interest_check:,.2f}[/bold]",
            style="bold",
        )

        console.print(table)

    # Disclaimer
    console.print(
        "\n[yellow]⚠️  UWAGA:[/yellow] Narzędzie nie stanowi porady prawnej.\n"
        "    Stawki należy zweryfikować i uaktualnić.\n"
        "    Skonsultuj się z prawnikiem w sprawie szczegółów Twojej sprawy.\n"
    )


@app.command(name="validate")
def validate_rates(
    rates_file: Path = typer.Argument(
        ...,
        help="Ścieżka do pliku CSV ze stawkami do walidacji",
        exists=True,
        file_okay=True,
        dir_okay=False,
    ),
) -> None:
    """
    Waliduje plik ze stawkami odsetek (sprawdza format, nakładanie się okresów, etc.).

    Przykład użycia:

    \b
    interest-calc validate data/rates_example.csv
    """
    try:
        console.print(f"\n[bold blue]🔍 Walidacja pliku:[/bold blue] {rates_file}\n")

        from interest_calc.rates import load_rates_from_csv

        rates = load_rates_from_csv(rates_file)

        console.print(f"[green]✓[/green] Plik jest poprawny!")
        console.print(f"[green]✓[/green] Wczytano {len(rates)} okresów stawek\n")

        # Wyświetl zakres dat
        if rates:
            min_date = min(r.valid_from for r in rates)
            max_date = max(r.valid_to for r in rates)
            console.print(f"Zakres dat: {min_date} do {max_date}\n")

            # Wyświetl tabelę stawek
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Data od", style="cyan")
            table.add_column("Data do", style="cyan")
            table.add_column("Stopa (%)", justify="right", style="yellow")

            for rate in rates:
                table.add_row(
                    str(rate.valid_from),
                    str(rate.valid_to),
                    f"{rate.annual_rate_percent:.2f}",
                )

            console.print(table)

    except Exception as e:
        console.print(f"\n[bold red]Błąd walidacji:[/bold red] {e}\n", style="red")
        raise typer.Exit(code=1)


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Wyświetl wersję programu",
        callback=version_callback,
        is_eager=True,
    ),
) -> None:
    """
    Kalkulator odsetek ustawowych za opóźnienie (Art. 481 KC) dla spraw frankowych.

    Narzędzie produkcyjnej jakości do obliczania odsetek z obsługą:
    - Różnych okresów stawek odsetek
    - Przepływów pieniężnych (cashflows)
    - Eksportu do CSV i XLSX
    - Pełnej walidacji danych
    """
    pass


if __name__ == "__main__":
    app()
