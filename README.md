# Interest Calculator - Kalkulator Odsetek Ustawowych Za Opóźnienie

**Produkcyjnej jakości narzędzie CLI + GUI w Pythonie** do obliczania odsetek ustawowych za opóźnienie (Art. 481 KC) dla spraw frankowych (CHF/PLN).

💻 **Dwa interfejsy:** Profesjonalny GUI (Streamlit) + Zaawansowany CLI (Typer)

## 📋 Spis treści

- [🖥️ GUI - Interfejs graficzny](#gui---interfejs-graficzny)
- [Funkcjonalności](#funkcjonalności)
- [Wymagania](#wymagania)
- [Instalacja](#instalacja)
- [Użycie](#użycie)
  - [GUI (Streamlit)](#gui-streamlit)
  - [CLI (Terminal)](#cli-terminal)
- [Przykłady](#przykłady)
- [Struktura projektu](#struktura-projektu)
- [Formaty plików](#formaty-plików)
- [Rozwój i testy](#rozwój-i-testy)
- [Uwagi prawne](#uwagi-prawne)

## 🖥️ GUI - Interfejs graficzny

**NOWE!** Profesjonalny interfejs graficzny zbudowany na Streamlit.

### Szybki start - GUI

```bash
# Zainstaluj zależności
pip install -e .

# Uruchom GUI
streamlit run streamlit_app.py
```

Aplikacja otworzy się automatycznie w przeglądarce na `http://localhost:8501`

### Zrzuty ekranu i funkcje GUI

![GUI Screenshot](https://via.placeholder.com/800x400?text=Professional+Calculator+GUI)

**Funkcje GUI:**
- ✅ **Intuicyjny formularz** - łatwe wprowadzanie danych
- ✅ **Upload plików** - przeciągnij i upuść CSV
- ✅ **Interaktywne tabele** - przejrzyste wyniki
- ✅ **Pobieranie raportów** - CSV i XLSX jednym kliknięciem
- ✅ **Responsywny design** - działa na każdym urządzeniu
- ✅ **3 zakładki:**
  - 📊 **Kalkulator** - główny interfejs obliczeń
  - 📖 **Instrukcja** - jak przygotować pliki danych
  - ℹ️ **O narzędziu** - informacje i disclaimer

**Interfejs zawiera:**
- Formularz z walidacją danych w czasie rzeczywistym
- Podsumowanie wyników w przejrzystych metrykach
- Szczegółową tabelę segmentów obliczeń
- Przyciski do pobrania raportów CSV/XLSX
- Ostrzeżenia prawne i disclaimery
- Sidebar z pomocą i informacjami

## ✨ Funkcjonalności

- ✅ **Obliczanie odsetek ustawowych** za opóźnienie zgodnie z Art. 481 KC
- ✅ **Obsługa zmian stawek** w czasie (piecewise calculation)
- ✅ **Przepływy pieniężne** (cashflows) - możliwość rozliczenia pełnej osi czasu płatności
- ✅ **Elastyczne zasady** liczenia dni (actual/365, actual/360, actual/actual)
- ✅ **Walidacja danych** - kompletna weryfikacja wejść
- ✅ **Raporty CSV i XLSX** z profesjonalnym formatowaniem
- ✅ **Czytelne podsumowanie** w terminalu z kolorowym formatowaniem
- ✅ **Type hints i Pydantic** - pełna typizacja i walidacja
- ✅ **Testy jednostkowe** z pytest
- ✅ **Profesjonalny GUI** zbudowany na Streamlit
- ✅ **Zaawansowany CLI** zbudowany na Typer

## 📦 Wymagania

- Python 3.9 lub nowszy
- pip (menedżer pakietów)

## 🚀 Instalacja

### Metoda 1: Instalacja z repozytorium (rozwojowa)

```bash
# Sklonuj repozytorium
git clone https://github.com/yourusername/expenseguard.git
cd expenseguard

# Zainstaluj w trybie deweloperskim
pip install -e ".[dev]"
```

### Metoda 2: Instalacja podstawowa

```bash
cd expenseguard
pip install -e .
```

### Weryfikacja instalacji

```bash
interest-calc --help
```

## 💻 Użycie

### GUI (Streamlit)

**Rekomendowane dla większości użytkowników** - łatwy w użyciu interfejs graficzny.

```bash
# Uruchom aplikację GUI
streamlit run streamlit_app.py
```

Następnie:
1. Otwórz przeglądarkę na `http://localhost:8501`
2. Wypełnij formularz
3. Prześlij pliki CSV (stawki i opcjonalnie przepływy)
4. Kliknij "OBLICZ ODSETKI"
5. Pobierz raport CSV lub XLSX

### CLI (Terminal)

**Dla zaawansowanych użytkowników** - pełna kontrola przez wiersz poleceń.

#### Podstawowa komenda

```bash
interest-calc calc \
  --principal-pln KWOTA \
  --start-date YYYY-MM-DD \
  --rates ścieżka/do/rates.csv
```

### Pełna lista opcji

| Opcja | Typ | Wymagane | Opis |
|-------|-----|----------|------|
| `--principal-pln` | float | ✅ | Główna kwota roszczenia w PLN |
| `--principal-chf` | float | ❌ | Równoważna kwota w CHF (informacyjnie) |
| `--fully-repaid` | bool | ❌ | Czy kredyt został spłacony w 100% |
| `--start-date` | YYYY-MM-DD | ✅ | Data początku opóźnienia |
| `--end-date` | YYYY-MM-DD | ❌ | Data końca naliczania (domyślnie: dziś) |
| `--cashflows` | ścieżka | ❌ | Plik CSV z przepływami pieniężnymi |
| `--rates` | ścieżka | ✅ | Plik CSV ze stawkami odsetek |
| `--basis` | actual/365 | ❌ | Zasady liczenia dni (domyślnie: actual/365) |
| `--output-dir` | ścieżka | ❌ | Katalog dla raportów (domyślnie: reports/) |
| `--no-report` | bool | ❌ | Nie generuj raportów, tylko wyświetl wynik |

## 📝 Przykłady

### Przykład 1: Podstawowe obliczenie

```bash
interest-calc calc \
  --principal-pln 112000 \
  --start-date 2022-05-10 \
  --rates interest_calc/data/rates_example.csv
```

### Przykład 2: Sprawa frankowa z przepływami

```bash
interest-calc calc \
  --principal-pln 112000 \
  --principal-chf 47000 \
  --start-date 2022-05-10 \
  --end-date 2023-05-10 \
  --cashflows interest_calc/data/cashflows_example.csv \
  --rates interest_calc/data/rates_example.csv \
  --fully-repaid
```

### Przykład 3: Sprawa z 2005 roku (placeholder dla daty pozwu)

```bash
# UWAGA: Podmień 2022-XX-XX na faktyczną datę doręczenia pozwu!
interest-calc calc \
  --principal-pln 112000 \
  --principal-chf 47000 \
  --start-date 2022-06-15 \
  --cashflows interest_calc/data/cashflows_example.csv \
  --rates interest_calc/data/rates_example.csv \
  --fully-repaid \
  --output-dir ./reports_case_2005
```

### Walidacja pliku ze stawkami

```bash
interest-calc validate interest_calc/data/rates_example.csv
```

## 📁 Struktura projektu

```
expenseguard/
├── streamlit_app.py          # ⭐ GUI (Streamlit) - NOWY!
├── interest_calc/
│   ├── __init__.py           # Inicjalizacja pakietu
│   ├── main.py               # CLI (Typer)
│   ├── models.py             # Modele Pydantic
│   ├── rates.py              # Loader i walidacja stawek
│   ├── engine.py             # Logika obliczeń
│   ├── report.py             # Generowanie raportów
│   ├── utils.py              # Funkcje pomocnicze
│   ├── data/
│   │   ├── rates_example.csv     # Przykładowe stawki
│   │   └── cashflows_example.csv # Przykładowe przepływy
│   └── tests/
│       ├── test_engine.py    # Testy silnika
│       ├── test_rates.py     # Testy stawek
│       └── test_cli.py       # Testy CLI
├── reports/                  # Katalog na wygenerowane raporty
├── pyproject.toml            # Konfiguracja projektu
├── .gitignore                # Wykluczenia Git
└── README.md                 # Ten plik
```

## 📄 Formaty plików

### Plik ze stawkami odsetek (`rates.csv`)

**Format:**
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

⚠️ **WAŻNE:** Plik `rates_example.csv` zawiera **PRZYKŁADOWE** stawki. Należy je **zaktualizować** zgodnie z oficjalnymi źródłami!

### Plik z przepływami (`cashflows.csv`)

**Format:**
```csv
date,amount_pln,direction
2005-06-01,112000.00,from_bank
2005-07-10,1200.00,from_client
2005-08-10,1180.00,from_client
```

**Wymagania:**
- Kolumny: `date`, `amount_pln`, `direction`
- `date`: Format `YYYY-MM-DD`
- `amount_pln`: Kwota w PLN (liczba dodatnia)
- `direction`: `from_bank` (wypłata) lub `from_client` (spłata)

**Przygotowanie pliku cashflows:**
1. Pobierz historię transakcji z banku
2. Wyodrębnij daty i kwoty wypłat oraz spłat
3. Zapisz w formacie CSV zgodnie z powyższym szablonem
4. Zweryfikuj poprawność dat i kwot

## 🔧 Rozwój i testy

### Uruchomienie testów

```bash
# Wszystkie testy
pytest

# Z pokryciem kodu
pytest --cov=interest_calc --cov-report=html

# Konkretny plik testowy
pytest interest_calc/tests/test_engine.py -v
```

### Kontrola jakości kodu

```bash
# Sprawdzenie typów (mypy)
mypy interest_calc

# Linting (ruff)
ruff check interest_calc

# Formatowanie (ruff)
ruff format interest_calc
```

### Struktura testów

- `test_engine.py` - Testy logiki obliczania odsetek
- `test_rates.py` - Testy wczytywania i walidacji stawek
- `test_cli.py` - Testy interfejsu CLI

## ⚖️ Uwagi prawne

### ⚠️ DISCLAIMER

**NARZĘDZIE NIE STANOWI PORADY PRAWNEJ**

To narzędzie służy wyłącznie celom obliczeniowym i informacyjnym. Nie zastępuje profesjonalnej porady prawnej ani księgowej.

### Ważne informacje:

1. **Weryfikacja stawek**: Stawki odsetek ustawowych za opóźnienie ulegają zmianom. Należy je **zawsze** weryfikować z oficjalnymi źródłami (NBP, Dziennik Ustaw).

2. **Konsultacja prawna**: Przed użyciem wyników w sprawach sądowych **skonsultuj się z prawnikiem** specjalizującym się w sprawach frankowych.

3. **Odpowiedzialność**: Autorzy nie ponoszą odpowiedzialności za ewentualne błędy w obliczeniach ani za decyzje podjęte na podstawie wyników tego narzędzia.

4. **Aktualizacja danych**: Użytkownik jest odpowiedzialny za aktualizację:
   - Pliku ze stawkami odsetek (`rates.csv`)
   - Danych o przepływach pieniężnych (`cashflows.csv`)

5. **Przypadki szczególne**: Niektóre sprawy mogą wymagać specyficznego podejścia (np. częściowe spłaty, umorzenia, konwersje). Narzędzie zakłada standardowe obliczenia.

## 📊 Algorytm obliczeń

Narzędzie implementuje następujący algorytm:

1. **Wczytanie stawek** z pliku `rates.csv`
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

## 🤝 Wsparcie

Jeśli masz pytania, sugestie lub znalazłeś błąd:

1. Sprawdź [dokumentację](#spis-treści)
2. Przejrzyj [przykłady](#przykłady)
3. Uruchom testy: `pytest -v`
4. Zgłoś problem przez Issues na GitHub

## 📜 Licencja

MIT License - Zobacz plik LICENSE dla szczegółów.

## 🎯 Roadmap

Przyszłe funkcjonalności:

- [ ] GUI (interfejs graficzny)
- [ ] Import danych z formatów bankowych (PDF, XLS)
- [ ] Automatyczne pobieranie aktualnych stawek z NBP
- [ ] Obsługa kapitalizacji odsetek
- [ ] Generowanie pism procesowych
- [ ] Wielojęzyczność (EN, DE)

---

**Wersja:** 1.0.0
**Ostatnia aktualizacja:** 2025-11-05
**Autor:** ExpenseGuard
