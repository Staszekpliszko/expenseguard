# ExpenseGuard

Program do obliczania przychodów i VAT dla małych firm i freelancerów.

## Funkcje

- **Faktury sprzedażowe** - zarządzanie fakturami przychodowymi z autouzupełnianiem klientów
- **Faktury kosztowe** - zarządzanie fakturami kosztowymi z konfigurowalnością odliczania VAT
- **Wyszukiwanie w bazie GUS** - automatyczne uzupełnianie danych firmy na podstawie NIP
- **Podsumowania podatkowe** - automatyczne obliczanie VAT, CIT/PIT, ZUS i kwoty "na rękę"
- **Ustawienia** - konfiguracja stawek VAT, CIT, ZUS i innych parametrów

## Technologie

- Electron + React
- SQLite (lokalna baza danych)
- Tailwind-inspired styling

## Instalacja

```bash
# Zainstaluj zależności
npm install

# Uruchom aplikację
npm start

# Tryb deweloperski (z DevTools)
npm run dev
```

## Jak używać wyszukiwania GUS

Przy dodawaniu nowego klienta lub dostawcy:
1. Wpisz NIP firmy w pole "NIP"
2. Kliknij przycisk "Wyszukaj w GUS"
3. Jeśli firma zostanie znaleziona, pola Nazwa i Adres zostaną automatycznie wypełnione danymi z bazy GUS

**Uwaga:** Domyślnie aplikacja używa testowego API GUS. Aby używać produkcyjnego API, potrzebujesz klucza API z GUS, który można uzyskać na stronie https://api.stat.gov.pl/Home/RegonApi

## Struktura projektu

```
.
├── main.js              # Proces główny Electron
├── preload.js           # Most IPC
├── package.json
├── src/
│   ├── backend/         # Logika backendu (Node.js)
│   │   ├── migrations.js
│   │   ├── database.js
│   │   ├── taxes.js
│   │   ├── invoices.js
│   │   └── gus.js       # Integracja z API GUS (REGON)
│   └── ui/              # Interfejs użytkownika (React)
│       ├── index.html
│       └── app.js
└── db/                  # Baza danych SQLite
    └── app.db
```

## Model danych

- **counterparties** - klienci i dostawcy
- **sales_invoices** / **sales_items** - faktury sprzedażowe
- **purchase_invoices** / **purchase_items** - faktury kosztowe
- **settings** - ustawienia aplikacji
- **payments** - płatności (opcjonalne)

## Obliczenia

### VAT
- VAT należny = suma VAT z faktur sprzedażowych
- VAT naliczony = suma VAT z faktur kosztowych × odliczalność
- VAT do zapłaty = VAT należny - VAT naliczony

### CIT/PIT
- Podstawa = przychód netto - koszty netto
- CIT/PIT = podstawa × stawka (z ustawień)

### Na rękę
- Przychód brutto - VAT do zapłaty - CIT/PIT - ZUS

## Licencja

MIT
