# Instrukcja instalacji i uruchomienia ExpenseGuard

## Krok 1: Pobierz kod

### Opcja A: Klonowanie przez Git
```bash
git clone https://github.com/Staszekpliszko/expenseguard.git
cd expenseguard
git checkout claude/invoice-tax-calculator-app-011CUpvH999eEpoongcj1GQQ
```

### Opcja B: Pobierz ZIP
1. Pobierz: https://github.com/Staszekpliszko/expenseguard/archive/refs/heads/claude/invoice-tax-calculator-app-011CUpvH999eEpoongcj1GQQ.zip
2. Rozpakuj archiwum
3. Otwórz terminal/wiersz poleceń w katalogu z aplikacją

## Krok 2: Zainstaluj Node.js (jeśli nie masz)

Sprawdź czy masz Node.js:
```bash
node --version
```

Jeśli nie masz, pobierz ze strony: https://nodejs.org/ (wersja LTS)

## Krok 3: Zainstaluj zależności

W katalogu aplikacji uruchom:
```bash
npm install
```

To może potrwać kilka minut.

## Krok 4: Uruchom aplikację

### Standardowe uruchomienie:
```bash
npm start
```

### Uruchomienie z DevTools (do debugowania):
```bash
npm run dev
```

## Rozwiązywanie problemów

### Problem: "SQLITE_CANTOPEN: unable to open database file"

**Rozwiązanie:** Folder `db/` musi istnieć. Utwórz go ręcznie:
```bash
mkdir db
```

Potem ponownie uruchom:
```bash
npm start
```

### Problem: "Cannot find module 'sqlite3'"

**Rozwiązanie:** Przeinstaluj zależności:
```bash
npm install
```

### Problem: Aplikacja się nie uruchamia

**Rozwiązanie:**
1. Sprawdź czy Node.js jest zainstalowany: `node --version`
2. Sprawdź czy jesteś w katalogu z `package.json`
3. Uruchom z DevTools: `npm run dev` i sprawdź błędy w konsoli

### Problem: Błąd przy `npm install` na Windows

**Rozwiązanie:** sqlite3 wymaga narzędzi kompilacji:
1. Zainstaluj Windows Build Tools:
   ```bash
   npm install --global windows-build-tools
   ```
2. Lub zainstaluj Visual Studio Build Tools ze strony Microsoft

## Pierwsze uruchomienie

Po pierwszym uruchomieniu aplikacja:
1. Utworzy folder `db/`
2. Utworzy bazę danych `app.db`
3. Zainicjalizuje tabele
4. Ustawi domyślne wartości:
   - Stawki VAT: 23%, 8%, 5%, 0%, 10%
   - CIT: 19%
   - ZUS: 1600 PLN
   - Termin płatności: 14 dni

## Struktura folderów po instalacji

```
expenseguard/
├── node_modules/       (po npm install)
├── db/                 (utworzony automatycznie)
│   └── app.db         (baza danych)
├── src/
│   ├── backend/
│   └── ui/
├── main.js
├── preload.js
└── package.json
```

## Dodawanie pierwszych danych

1. **Dodaj klienta/dostawcę:**
   - Wpisz nazwę w polu autouzupełniania
   - Jeśli nie istnieje, musisz go najpierw dodać do bazy (w przyszłości będzie przycisk "Dodaj nowego")
   - **Tymczasowe rozwiązanie:** Możesz dodać testowego klienta przez SQLite CLI lub poczekać na aktualizację

2. **Dodaj fakturę:**
   - Przejdź do zakładki "Faktury - Przychód" lub "Faktury - Kosztowe"
   - Kliknij "Dodaj fakturę"
   - Wypełnij formularz
   - Dodaj pozycje
   - Kliknij "Zapisz"

3. **Zobacz podsumowanie:**
   - Przejdź do zakładki "Podatki"
   - Wybierz rok i miesiąc
   - Kliknij "Przelicz"

## Kontakt i wsparcie

Zgłaszaj problemy na: https://github.com/Staszekpliszko/expenseguard/issues
