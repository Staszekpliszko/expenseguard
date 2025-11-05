"""
Streamlit GUI dla kalkulatora odsetek ustawowych za opóźnienie.

Profesjonalny interfejs graficzny do obliczania odsetek ustawowych
za opóźnienie (Art. 481 KC) dla spraw frankowych CHF/PLN.

Uruchomienie:
    streamlit run streamlit_app.py
"""

from datetime import date, datetime
from io import BytesIO
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Optional

import pandas as pd
import streamlit as st

from interest_calc.engine import calculate_interest
from interest_calc.models import DayCountBasis, Settings
from interest_calc.report import create_segments_dataframe, create_summary_dict

# Konfiguracja strony
st.set_page_config(
    page_title="Kalkulator Odsetek Ustawowych",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS dla profesjonalnego wyglądu
st.markdown(
    """
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #555;
        text-align: center;
        margin-bottom: 2rem;
    }
    .result-box {
        background-color: #f0f8ff;
        border-left: 5px solid #1f77b4;
        padding: 1.5rem;
        margin: 1rem 0;
        border-radius: 5px;
    }
    .warning-box {
        background-color: #fff3cd;
        border-left: 5px solid #ffc107;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 5px;
    }
    .success-box {
        background-color: #d4edda;
        border-left: 5px solid #28a745;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 5px;
    }
    .stButton>button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
        font-size: 1.1rem;
        padding: 0.75rem;
        border-radius: 5px;
    }
    .stButton>button:hover {
        background-color: #155a8a;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def main() -> None:
    """Główna funkcja aplikacji Streamlit."""

    # Header
    st.markdown(
        '<div class="main-header">💰 Kalkulator Odsetek Ustawowych Za Opóźnienie</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="sub-header">Art. 481 KC - Sprawy Frankowe CHF/PLN</div>',
        unsafe_allow_html=True,
    )

    # Sidebar z informacjami
    with st.sidebar:
        st.image(
            "https://img.icons8.com/color/96/calculator--v1.png",
            width=80,
            use_container_width=False,
        )
        st.markdown("### 📋 Informacje")
        st.info(
            """
            **Kalkulator odsetek** pozwala obliczyć odsetki ustawowe
            za opóźnienie zgodnie z Art. 481 KC dla spraw frankowych.

            **Funkcje:**
            - ✅ Obliczenia z różnymi stawkami
            - ✅ Przepływy pieniężne
            - ✅ Raporty CSV i XLSX
            - ✅ Walidacja danych
            """
        )

        st.markdown("### 📚 Jak używać")
        with st.expander("Krok po kroku"):
            st.markdown(
                """
                1. **Wypełnij formularz** - podaj kwotę i daty
                2. **Prześlij plik stawek** - CSV z okresami i stopami
                3. **(Opcjonalnie)** Prześlij przepływy pieniężne
                4. **Kliknij "Oblicz Odsetki"**
                5. **Pobierz raport** - CSV lub XLSX
                """
            )

        st.markdown("### ⚠️ Disclaimer")
        st.warning(
            """
            Narzędzie **nie stanowi** porady prawnej.
            Stawki należy zweryfikować. Skonsultuj się z prawnikiem.
            """
        )

        st.markdown("---")
        st.markdown("**Wersja:** 1.0.0")
        st.markdown("**© 2025 ExpenseGuard**")

    # Główna zawartość
    tab1, tab2, tab3 = st.tabs(["📊 Kalkulator", "📖 Instrukcja", "ℹ️ O narzędziu"])

    with tab1:
        render_calculator_tab()

    with tab2:
        render_instructions_tab()

    with tab3:
        render_about_tab()


def render_calculator_tab() -> None:
    """Renderuje zakładkę kalkulatora."""

    st.markdown("## Formularz obliczeń")

    # Formularz w kolumnach
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 💵 Kwoty")
        principal_pln = st.number_input(
            "Kwota główna (PLN) *",
            min_value=0.01,
            value=112000.0,
            step=1000.0,
            help="Główna kwota roszczenia w PLN",
        )

        principal_chf = st.number_input(
            "Kwota główna (CHF)",
            min_value=0.0,
            value=47000.0,
            step=1000.0,
            help="Równoważna kwota w CHF (tylko informacyjnie)",
        )
        if principal_chf == 0.0:
            principal_chf = None

        fully_repaid = st.checkbox(
            "Kredyt spłacony w 100%", value=False, help="Czy kredyt został w pełni spłacony"
        )

    with col2:
        st.markdown("### 📅 Okres")
        start_date = st.date_input(
            "Data początku opóźnienia *",
            value=date(2022, 5, 10),
            help="Data doręczenia wezwania/pozwu",
        )

        end_date = st.date_input(
            "Data końca naliczania", value=date.today(), help="Domyślnie: dziś"
        )

        basis = st.selectbox(
            "Sposób liczenia dni",
            options=["actual/365", "actual/360", "actual/actual"],
            index=0,
            help="Podstawa obliczeń",
        )

    # Upload plików
    st.markdown("### 📁 Pliki danych")

    col3, col4 = st.columns(2)

    with col3:
        rates_file = st.file_uploader(
            "Plik ze stawkami odsetek (CSV) *",
            type=["csv"],
            help="Format: valid_from,valid_to,annual_rate_percent",
        )

        if rates_file is None:
            st.info(
                "💡 Możesz użyć przykładowego pliku stawek - "
                "pobierz z `interest_calc/data/rates_example.csv`"
            )

    with col4:
        cashflows_file = st.file_uploader(
            "Plik z przepływami pieniężnymi (CSV)",
            type=["csv"],
            help="Format: date,amount_pln,direction",
        )

        if cashflows_file is None:
            st.info(
                "💡 Opcjonalnie: możesz dodać plik z przepływami - "
                "pobierz przykład z `interest_calc/data/cashflows_example.csv`"
            )

    # Przycisk oblicz
    st.markdown("---")

    calculate_button = st.button("🔢 OBLICZ ODSETKI", type="primary", use_container_width=True)

    # Obliczenia
    if calculate_button:
        if rates_file is None:
            st.error("❌ Musisz przesłać plik ze stawkami odsetek!")
            return

        try:
            # Zapisz pliki tymczasowe
            with NamedTemporaryFile(delete=False, suffix=".csv") as tmp_rates:
                tmp_rates.write(rates_file.read())
                rates_path = Path(tmp_rates.name)

            cashflows_path: Optional[Path] = None
            if cashflows_file is not None:
                with NamedTemporaryFile(delete=False, suffix=".csv") as tmp_cashflows:
                    tmp_cashflows.write(cashflows_file.read())
                    cashflows_path = Path(tmp_cashflows.name)

            # Utwórz settings
            settings = Settings(
                principal_pln=principal_pln,
                principal_chf=principal_chf,
                fully_repaid=fully_repaid,
                start_date=start_date,
                end_date=end_date,
                cashflows_file=cashflows_path,
                rates_file=rates_path,
                basis=DayCountBasis(basis),
            )

            # Oblicz
            with st.spinner("⏳ Obliczam odsetki..."):
                result = calculate_interest(settings)

            # Wyświetl wyniki
            display_results(result)

            # Cleanup
            rates_path.unlink()
            if cashflows_path:
                cashflows_path.unlink()

        except Exception as e:
            st.error(f"❌ Błąd podczas obliczeń: {e}")
            st.exception(e)


def display_results(result) -> None:
    """Wyświetla wyniki obliczeń."""

    st.markdown("---")
    st.markdown("## 📊 Wyniki obliczeń")

    # Podsumowanie
    st.markdown('<div class="success-box">', unsafe_allow_html=True)
    st.markdown("### ✅ Obliczenia zakończone pomyślnie!")
    st.markdown("</div>", unsafe_allow_html=True)

    # Box z wynikami
    summary = create_summary_dict(result)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Kwota główna (PLN)", f"{summary['Kwota główna (PLN)']:,.2f} PLN")
        st.metric("Liczba dni", f"{summary['Liczba dni']:,}")

    with col2:
        st.metric("Łączne odsetki (PLN)", f"{summary['Łączne odsetki (PLN)']:,.2f} PLN")
        st.metric("Średnia ważona stopa", f"{summary['Średnia ważona stopa (%)']:.4f}%")

    with col3:
        st.metric("Łączne roszczenie (PLN)", f"{summary['Łączne roszczenie (PLN)']:,.2f} PLN")
        st.metric("Liczba okresów stawek", f"{summary['Liczba okresów stawek']:,}")

    # Tabela segmentów
    st.markdown("### 📋 Szczegółowe segmenty obliczeń")

    segments_df = create_segments_dataframe(result)

    # Sformatuj DataFrame dla lepszego wyświetlania
    display_df = segments_df.copy()

    # Formatuj kolumny numeryczne
    if "Dni" in display_df.columns:
        display_df["Dni"] = display_df["Dni"].apply(lambda x: f"{x:,}" if x != "" else "")

    if "Stopa (%)" in display_df.columns:
        display_df["Stopa (%)"] = display_df["Stopa (%)"].apply(
            lambda x: f"{x:.2f}" if isinstance(x, (int, float)) else x
        )

    if "Podstawa (PLN)" in display_df.columns:
        display_df["Podstawa (PLN)"] = display_df["Podstawa (PLN)"].apply(
            lambda x: f"{x:,.2f}" if isinstance(x, (int, float)) else x
        )

    if "Odsetki (PLN)" in display_df.columns:
        display_df["Odsetki (PLN)"] = display_df["Odsetki (PLN)"].apply(
            lambda x: f"{x:,.2f}" if isinstance(x, (int, float)) else x
        )

    st.dataframe(display_df, use_container_width=True, hide_index=True)

    # Przyciski do pobrania raportów
    st.markdown("### 💾 Pobierz raporty")

    col1, col2 = st.columns(2)

    with col1:
        # CSV
        csv_buffer = BytesIO()
        segments_df.to_csv(csv_buffer, index=False, encoding="utf-8")
        csv_data = csv_buffer.getvalue()

        st.download_button(
            label="📄 Pobierz CSV",
            data=csv_data,
            file_name=f"interest_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with col2:
        # XLSX
        xlsx_buffer = BytesIO()
        with pd.ExcelWriter(xlsx_buffer, engine="openpyxl") as writer:
            # Podsumowanie
            summary_df = pd.DataFrame(
                [{"Parametr": k, "Wartość": v} for k, v in summary.items()]
            )
            summary_df.to_excel(writer, sheet_name="Podsumowanie", index=False)

            # Segmenty
            segments_df.to_excel(writer, sheet_name="Segmenty", index=False)

        xlsx_data = xlsx_buffer.getvalue()

        st.download_button(
            label="📊 Pobierz XLSX",
            data=xlsx_data,
            file_name=f"interest_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

    # Disclaimer
    st.markdown('<div class="warning-box">', unsafe_allow_html=True)
    st.markdown(
        """
        **⚠️ UWAGA:** Narzędzie nie stanowi porady prawnej.
        Stawki należy zweryfikować i uaktualnić.
        Skonsultuj się z prawnikiem w sprawie szczegółów Twojej sprawy.
        """
    )
    st.markdown("</div>", unsafe_allow_html=True)


def render_instructions_tab() -> None:
    """Renderuje zakładkę z instrukcjami."""

    st.markdown("## 📖 Instrukcja użycia")

    st.markdown(
        """
        ### Krok 1: Przygotuj plik ze stawkami odsetek

        Plik CSV z stawkami odsetek ustawowych za opóźnienie powinien mieć format:

        ```csv
        valid_from,valid_to,annual_rate_percent
        2022-01-01,2022-06-30,10.0
        2022-07-01,2022-12-31,12.0
        ```

        **Wymagania:**
        - Kolumny: `valid_from`, `valid_to`, `annual_rate_percent`
        - Daty w formacie `YYYY-MM-DD`
        - Stawki jako liczby dziesiętne (10.0 = 10%)
        - Okresy nie mogą się nakładać
        - Okresy muszą pokrywać cały zakres obliczeń

        **Źródła oficjalnych stawek:**
        - [Narodowy Bank Polski (NBP)](https://nbp.pl)
        - Dziennik Ustaw RP
        - Portal informacyjny rządu RP

        ⚠️ **WAŻNE:** Stawki należy **zweryfikować** z oficjalnymi źródłami!
        """
    )

    st.markdown("---")

    st.markdown(
        """
        ### Krok 2: (Opcjonalnie) Przygotuj plik z przepływami

        Plik CSV z przepływami pieniężnymi powinien mieć format:

        ```csv
        date,amount_pln,direction
        2005-06-01,112000.00,from_bank
        2005-07-10,1200.00,from_client
        ```

        **Wymagania:**
        - Kolumny: `date`, `amount_pln`, `direction`
        - `date`: Format `YYYY-MM-DD`
        - `amount_pln`: Kwota w PLN (liczba dodatnia)
        - `direction`: `from_bank` (wypłata) lub `from_client` (spłata)
        """
    )

    st.markdown("---")

    st.markdown(
        """
        ### Krok 3: Wypełnij formularz

        1. **Kwota główna (PLN)** - główna kwota roszczenia
        2. **Kwota główna (CHF)** - opcjonalnie, dla informacji
        3. **Data początku opóźnienia** - data doręczenia pozwu/wezwania
        4. **Data końca naliczania** - domyślnie dzisiaj
        5. **Prześlij pliki** - stawki (wymagane), przepływy (opcjonalnie)
        """
    )

    st.markdown("---")

    st.markdown(
        """
        ### Krok 4: Oblicz i pobierz raport

        1. Kliknij **"OBLICZ ODSETKI"**
        2. Sprawdź wyniki w tabeli
        3. Pobierz raport w formacie CSV lub XLSX
        """
    )


def render_about_tab() -> None:
    """Renderuje zakładkę o narzędziu."""

    st.markdown("## ℹ️ O narzędziu")

    st.markdown(
        """
        ### Kalkulator Odsetek Ustawowych Za Opóźnienie

        **Wersja:** 1.0.0
        **Data wydania:** 2025-11-05
        **Autor:** ExpenseGuard

        ---

        ### Funkcjonalności

        - ✅ **Obliczanie odsetek ustawowych** za opóźnienie zgodnie z Art. 481 KC
        - ✅ **Obsługa zmian stawek** w czasie (piecewise calculation)
        - ✅ **Przepływy pieniężne** - możliwość rozliczenia pełnej osi czasu płatności
        - ✅ **Elastyczne zasady** liczenia dni (actual/365, actual/360, actual/actual)
        - ✅ **Walidacja danych** - kompletna weryfikacja wejść
        - ✅ **Raporty CSV i XLSX** z profesjonalnym formatowaniem
        - ✅ **Profesjonalny GUI** zbudowany na Streamlit

        ---

        ### Technologie

        - **Python 3.9+**
        - **Streamlit** - interfejs graficzny
        - **Pydantic** - walidacja danych
        - **Pandas** - przetwarzanie danych
        - **OpenPyXL** - generowanie XLSX
        - **Typer** - CLI

        ---

        ### Algorytm obliczeń

        Narzędzie implementuje następujący algorytm:

        1. **Wczytanie stawek** z pliku CSV
        2. **Walidacja** okresów stawek (brak luk, brak nakładania)
        3. **Utworzenie segmentów** dla okresu [start_date, end_date)
        4. **Dla każdej podstawy** (principal lub cashflow):
           - Obliczenie odsetek piecewise przez wszystkie segmenty
           - Wzór: `interest = principal × (rate/100) × (days/365)`
        5. **Agregacja** wyników i generowanie raportów

        **Konwencja dat:**
        - Data początkowa jest **włączona** (inclusive)
        - Data końcowa jest **wyłączona** (exclusive)
        - Standard: `[start_date, end_date)`

        **Brak kapitalizacji:**
        - Odsetki są liczone od kwoty głównej
        - Odsetki **NIE** są kapitalizowane (dodawane do podstawy)

        ---

        ### Licencja

        MIT License

        ---

        ### Wsparcie

        Jeśli masz pytania lub znalazłeś błąd:
        - Sprawdź dokumentację w zakładce "Instrukcja"
        - Zgłoś problem przez Issues na GitHub

        ---

        ### ⚠️ Disclaimer prawny

        **NARZĘDZIE NIE STANOWI PORADY PRAWNEJ**

        To narzędzie służy wyłącznie celom obliczeniowym i informacyjnym.
        Nie zastępuje profesjonalnej porady prawnej ani księgowej.

        **Ważne informacje:**

        1. **Weryfikacja stawek**: Stawki odsetek ustawowych za opóźnienie ulegają zmianom.
           Należy je **zawsze** weryfikować z oficjalnymi źródłami (NBP, Dziennik Ustaw).

        2. **Konsultacja prawna**: Przed użyciem wyników w sprawach sądowych
           **skonsultuj się z prawnikiem** specjalizującym się w sprawach frankowych.

        3. **Odpowiedzialność**: Autorzy nie ponoszą odpowiedzialności za ewentualne błędy
           w obliczeniach ani za decyzje podjęte na podstawie wyników tego narzędzia.

        4. **Aktualizacja danych**: Użytkownik jest odpowiedzialny za aktualizację:
           - Pliku ze stawkami odsetek (`rates.csv`)
           - Danych o przepływach pieniężnych (`cashflows.csv`)

        5. **Przypadki szczególne**: Niektóre sprawy mogą wymagać specyficznego podejścia
           (np. częściowe spłaty, umorzenia, konwersje). Narzędzie zakłada standardowe obliczenia.
        """
    )


if __name__ == "__main__":
    main()
