# 📊 Konwerter PDF Bank Millennium CHF - Instrukcja Budowania EXE

## 🔧 Problem i Rozwiązanie

### Problem oryginalny:
```
AttributeError: 'NoneType' object has no attribute 'buffer'
```

**Przyczyna:** W aplikacji GUI skompilowanej do `.exe`, `sys.stdout` i `sys.stderr` są `None` (brak konsoli).

### Zastosowane rozwiązanie:
✅ Dodano zabezpieczenie sprawdzające czy `stdout/stderr` istnieją przed użyciem
✅ Przekierowanie logów do plików w środowisku exe
✅ Fallback do `io.StringIO()` w przypadku błędów

---

## 📋 Wymagania

### 1. Python
- **Wersja:** Python 3.8 lub nowszy
- **Pobierz:** https://www.python.org/downloads/
- ⚠️ **WAŻNE:** Zaznacz "Add Python to PATH" podczas instalacji

### 2. Sprawdź instalację
Otwórz Command Prompt (cmd) i wpisz:
```cmd
python --version
pip --version
```

Jeśli widzisz numery wersji - wszystko OK! ✓

---

## 🚀 Jak zbudować EXE?

### Metoda 1: Automatyczny Build (ZALECANA)

1. **Skopiuj wszystkie pliki do folderu** `D:\MOJE\MILLENIUM CHF\`:
   - `pdf_converter_gui.py` ← naprawiona wersja
   - `pdf_to_csv.py` ← naprawiona wersja
   - `requirements.txt`
   - `pdf_converter_gui.spec`
   - `build_exe.bat`

2. **Uruchom build:**
   ```cmd
   cd D:\MOJE\MILLENIUM CHF
   build_exe.bat
   ```

3. **Poczekaj** (2-5 minut)

4. **Gotowe!** Plik exe znajdziesz w:
   ```
   D:\MOJE\MILLENIUM CHF\dist\PDF_Converter_Millennium_CHF.exe
   ```

---

### Metoda 2: Quick Build (bez virtualenv)

Jeśli Metoda 1 nie działa:
```cmd
cd D:\MOJE\MILLENIUM CHF
build_exe_simple.bat
```

---

### Metoda 3: Ręczny Build

```cmd
cd D:\MOJE\MILLENIUM CHF

# Zainstaluj zależności
pip install -r requirements.txt

# Zbuduj exe
pyinstaller pdf_converter_gui.spec
```

---

## 📦 Co zawiera paczka?

```
D:\MOJE\MILLENIUM CHF\
│
├── pdf_converter_gui.py       ← Główny program GUI (NAPRAWIONY)
├── pdf_to_csv.py              ← Parser PDF-ów (NAPRAWIONY)
├── requirements.txt           ← Lista zależności
├── pdf_converter_gui.spec     ← Konfiguracja PyInstaller
├── build_exe.bat              ← Automatyczny build (z venv)
├── build_exe_simple.bat       ← Szybki build (bez venv)
└── README_BUILD.md            ← Ta instrukcja
```

---

## ✅ Jak używać EXE?

1. **Uruchom:** `PDF_Converter_Millennium_CHF.exe`
2. **Wybierz PDF-y** przyciskiem "Wybierz PDF-y"
3. **Wybierz tryb:**
   - Nowy plik ← tworzy nowe CSV/Excel
   - Dopisz ← dodaje do istniejącego
4. **Kliknij:** "Rozpocznij konwersję"
5. **Gotowe!** Pliki CSV/Excel są w wybranym folderze

---

## 🛠️ Rozwiązywanie Problemów

### Problem: "Python nie jest rozpoznawany..."
**Rozwiązanie:**
1. Zainstaluj Python z: https://www.python.org/downloads/
2. Podczas instalacji ZAZNACZ: ☑️ "Add Python to PATH"
3. Zrestartuj komputer
4. Sprawdź: `python --version`

### Problem: "pip install nie działa"
**Rozwiązanie:**
```cmd
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Problem: "PyInstaller: command not found"
**Rozwiązanie:**
```cmd
pip install pyinstaller
```

### Problem: Antywirus blokuje exe
**Rozwiązanie:**
- To normalne dla nowo zbudowanych exe
- Dodaj folder `dist\` do wyjątków antywirusa
- Lub użyj certyfikatu do podpisania exe

### Problem: Exe się nie uruchamia
**Rozwiązanie:**
1. Sprawdź logi w folderze z exe:
   - `app_stdout.log`
   - `app_stderr.log`
   - `pdf_converter.log`
2. Uruchom w trybie debug:
   ```cmd
   PDF_Converter_Millennium_CHF.exe > debug.log 2>&1
   ```

---

## 📝 Zmiany w kodzie (naprawki)

### W `pdf_converter_gui.py` (linia 30-54):
```python
# PRZED (BŁędne):
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

# PO (Poprawne):
if sys.stdout is not None and hasattr(sys.stdout, 'buffer'):
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
elif sys.stdout is None:
    log_dir = os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else __file__)
    log_file = os.path.join(log_dir, 'app_stdout.log')
    sys.stdout = open(log_file, 'w', encoding='utf-8', buffering=1)
```

### W `pdf_to_csv.py` (linia 268-290):
Identyczna poprawka.

---

## 🎯 Konfiguracja PyInstaller

Plik `.spec` zawiera:
- ✅ `console=False` - bez okna konsoli (GUI)
- ✅ `onefile=True` - jeden plik exe
- ✅ Wszystkie wymagane biblioteki
- ✅ Optymalizacja UPX

---

## 📊 Struktura po zbudowaniu

```
D:\MOJE\MILLENIUM CHF\
│
├── dist\
│   └── PDF_Converter_Millennium_CHF.exe  ← Gotowy program!
│
├── build\                                 ← Pliki tymczasowe (można usunąć)
├── venv\                                  ← Środowisko wirtualne (można usunąć)
└── ... (pliki źródłowe)
```

---

## 💡 Porady

1. **Dystrybuuj tylko plik EXE** z folderu `dist\`
2. **Rozmiar exe:** ~50-80 MB (zawiera Python + biblioteki)
3. **Pierwsze uruchomienie:** Może trwać dłużej (rozpakowywanie)
4. **Logi:** Sprawdzaj pliki `.log` w razie problemów
5. **Aktualizacje:** Po zmianie kodu uruchom `build_exe.bat` ponownie

---

## 🔒 Bezpieczeństwo

- Program NIE wysyła danych przez internet
- Przetwarza PDF-y lokalnie na Twoim komputerze
- Tworzy pliki CSV/Excel tylko w wybranym folderze
- Kod źródłowy jest otwarty i dostępny do przeglądu

---

## 📧 Wsparcie

Jeśli napotkasz problemy:
1. Sprawdź sekcję "Rozwiązywanie Problemów" powyżej
2. Przejrzyj logi: `pdf_converter.log`, `app_stdout.log`
3. Sprawdź czy Python i pip są zainstalowane poprawnie

---

## ✨ Co dalej?

Po zbudowaniu exe możesz:
- 📁 Skopiować exe na inne komputery (nie potrzebują Python!)
- 💾 Utworzyć skrót na pulpicie
- 📤 Udostępnić znajomym/rodzinie
- 🎨 Dodać własną ikonę (zmień w `.spec`: `icon='icon.ico'`)

---

**Autor poprawek:** Claude AI
**Data:** 2025-11-05
**Wersja:** 1.1 (z poprawkami sys.stdout)
