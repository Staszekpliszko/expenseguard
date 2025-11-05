#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Skrypt do konwersji PDF-ów Bank Millennium CHF na CSV/Excel
Autor: Claude
Data: 2025-11-04
Poprawki: 2025-11-05 - Fix dla kompilacji do exe
"""

import os
import re
import sys
import io
from datetime import datetime
from pathlib import Path
import pdfplumber
import pandas as pd
from typing import List, Dict, Optional
import logging

# Konfiguracja logowania
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pdf_converter.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class BankMillenniumPDFParser:
    """Klasa do parsowania PDF-ów z Bank Millennium"""

    def __init__(self):
        self.transactions = []

    def parse_date(self, date_str: str) -> Optional[str]:
        """Parsuje datę z różnych formatów do YYYY-MM-DD"""
        if not date_str:
            return None

        # Usuń białe znaki
        date_str = date_str.strip()

        # Mapowanie polskich miesięcy
        polish_months = {
            'sty': '01', 'lut': '02', 'mar': '03', 'kwi': '04',
            'maj': '05', 'cze': '06', 'lip': '07', 'sie': '08',
            'wrz': '09', 'paź': '10', 'lis': '11', 'gru': '12'
        }

        # Format: "18 paź 2025" lub "18 października 2025"
        match = re.search(r'(\d{1,2})\s+(\w+)\s+(\d{4})', date_str, re.IGNORECASE)
        if match:
            day, month_str, year = match.groups()
            month_str_lower = month_str.lower()[:3]
            month = polish_months.get(month_str_lower)
            if month:
                return f"{year}-{month}-{day.zfill(2)}"

        # Format: "2025-10-18" lub "18/10/2025" lub "18.10.2025"
        match = re.search(r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})', date_str)
        if match:
            year, month, day = match.groups()
            return f"{year}-{month.zfill(2)}-{day.zfill(2)}"

        match = re.search(r'(\d{1,2})[/.-](\d{1,2})[/.-](\d{4})', date_str)
        if match:
            day, month, year = match.groups()
            return f"{year}-{month.zfill(2)}-{day.zfill(2)}"

        logger.warning(f"Nie można sparsować daty: {date_str}")
        return None

    def parse_amount(self, amount_str: str) -> Optional[float]:
        """Parsuje kwotę z formatu '1 234,56', '1.234,56', '1.165.20' lub '1234.56'"""
        if not amount_str or amount_str.strip() == '-':
            return None

        original_str = amount_str
        amount_str = amount_str.strip()

        # Usuń znaki walut
        amount_str = re.sub(r'(CHF|PLN|EUR)', '', amount_str, flags=re.IGNORECASE).strip()

        # Sprawdź format: jeśli jest przecinek, to kropki są separatorami tysięcy
        if ',' in amount_str:
            # Format: 1.234,56 lub 1 234,56
            amount_str = amount_str.replace(' ', '').replace('.', '').replace(',', '.')
        else:
            # Format bez przecinka
            dots = amount_str.count('.')
            if dots >= 2:
                # Format: 1.234.567 lub 1.165.20 - kropki są separatorami tysięcy
                # Usuń wszystkie kropki oprócz ostatniej (która może być dziesiętną)
                parts = amount_str.split('.')
                if len(parts[-1]) == 2:
                    # Ostatnie 2 cyfry to grosze: 1.165.20 -> 116520
                    amount_str = ''.join(parts[:-1]) + '.' + parts[-1]
                else:
                    # Wszystkie kropki to separatory: 1.234.567 -> 1234567
                    amount_str = amount_str.replace('.', '')
            elif dots == 1:
                # Jedna kropka - sprawdź czy to separator tysięcy czy dziesiętny
                parts = amount_str.split('.')
                if len(parts) == 2:
                    # Jeśli jest 3 cyfry po kropce i nie są to wszystkie cyfry, to separator tysięcy
                    if len(parts[1]) == 3 and len(parts[0]) > 0:
                        # 1.234 -> 1234
                        amount_str = amount_str.replace('.', '')
                    elif len(parts[1]) == 2:
                        # 1234.56 -> zostaw jako jest (kropka dziesiętna)
                        pass
                    else:
                        # Inne - zostaw jako jest
                        pass

        # Usuń pozostałe białe znaki i niechciane znaki
        amount_str = amount_str.replace(' ', '')
        amount_str = re.sub(r'[^\d.-]', '', amount_str)

        try:
            return float(amount_str)
        except ValueError:
            logger.warning(f"Nie można sparsować kwoty: {original_str} (po przetworzeniu: {amount_str})")
            return None

    def parse_percentage(self, percent_str: str) -> Optional[float]:
        """Parsuje stopę procentową z formatu '2,41200%'"""
        if not percent_str:
            return None

        # Usuń '%' i białe znaki
        percent_str = percent_str.strip().replace('%', '').replace(',', '.')

        try:
            return float(percent_str)
        except ValueError:
            return None

    def extract_from_text(self, text: str, pdf_path: str) -> List[Dict]:
        """Ekstrahuje transakcje z tekstu PDF"""
        transactions = []

        # Usuń łamanie linii i znaki unicode
        text = text.replace('\n', ' ').replace('�', '')

        # Podziel tekst na bloki transakcji po "Potwierdzenie wykonania operacji"
        blocks = re.split(r'Potwierdzenie wykonania operacji', text)

        for block in blocks:
            if len(block) < 50:  # Zbyt krótki blok
                continue

            # Szukaj daty transakcji (format: 2022-04-22)
            date_match = re.search(r'Datatransakcji\s*(\d{4}-\d{2}-\d{2})', block)
            if not date_match:
                continue

            parsed_date = date_match.group(1)

            # Szukaj typu transakcji (obsługa różnych enkodowań polskich znaków)
            operation_type = None
            # SPŁ może być: SPŁ, SP�, SPL, SP
            if re.search(r'SP[L�Ł�]?[\.\s]?RATY[-\s]?REGULARNA', block, re.IGNORECASE):
                operation_type = 'SPŁ.RATY-REGULARNA'
            elif re.search(r'SP[L�Ł�]?[\.\s]?RATY[-\s]?NIEREGULARNA', block, re.IGNORECASE):
                operation_type = 'SP.RATY-NIEREGULARNA'
            elif re.search(r'ZMIANA\s*STOPY', block, re.IGNORECASE):
                operation_type = 'ZMIANA STOPY PROC.'
            elif re.search(r'ODSETKI\s*PRZETERMINOWANE', block, re.IGNORECASE):
                operation_type = 'ODSETKI PRZETERMINOWANE'

            if not operation_type:
                continue

            # Szukaj kwot
            capital_chf = None
            interest_chf = None
            overdue_interest_chf = None
            total_chf = None
            amount_pln = None
            interest_rate = None

            # Kwota transakcji (zazwyczaj kapitał)
            trans_amount = re.search(r'Kwotatransakcji\s*([\d,\.]+)\s*CHF', block)
            if trans_amount:
                capital_chf = self.parse_amount(trans_amount.group(1))

            # Odsetki - różne formaty (z lub bez spacji, różne enkodowania KAPITAŁ)
            # Format 1: "ODSETKI 1.73"
            # Format 2: "ODSETKI1.73"
            # Format 3: "KAPITAŁODSETKI1.73" - po KAPITAŁ następuje ODSETKI i liczba
            interest_match = re.search(r'ODSETKI\s*([\d,\.]+)', block, re.IGNORECASE)
            if not interest_match:
                # Szukaj po KAPITA� lub KAPITAŁ
                interest_match = re.search(r'KAPITA[L�Ł�].*?ODSETKI\s*([\d,\.]+)', block, re.IGNORECASE)
            if interest_match:
                interest_chf = self.parse_amount(interest_match.group(1))

            # Odsetki przeterminowane
            overdue_match = re.search(r'ODSETKIPRZETERMINOWANE\s*([\d,\.]+)', block)
            if overdue_match:
                overdue_interest_chf = self.parse_amount(overdue_match.group(1))

            # Kwota raty (kapitał + odsetki) - format: "KWOTARATY(KAPITAŁ+ODSETKI)263.47"
            total_match = re.search(r'KWOTARATY[^\d]*([\d,\.]+)', block)
            if total_match:
                total_chf = self.parse_amount(total_match.group(1))

            # Kwota w PLN - szukaj różnych wariantów
            pln_match = re.search(r'RATYKREDYTUPLN([\d\.,]+)', block)
            if not pln_match:
                pln_match = re.search(r'PLN([\d\.,]+)', block)
            if not pln_match:
                # Szukaj kwoty przed "PLN"
                pln_match = re.search(r'([\d\.,]+)PLN', block)
            if pln_match:
                # PLN może być w formacie amerykańskim: 1,165.20
                pln_str = pln_match.group(1)
                # Jeśli ma przecinek I kropkę, to przecinek to separator tysięcy
                if ',' in pln_str and '.' in pln_str:
                    # Format: 1,165.20 (amerykański)
                    pln_str = pln_str.replace(',', '')
                amount_pln = self.parse_amount(pln_str)

            # Stopa procentowa
            # Dla zmian stóp szukaj NOWEJ stopy
            if operation_type == 'ZMIANA STOPY PROC.':
                new_rate_match = re.search(r'NOWASTOPAPROCENTOWA\s*([\d,\.]+)', block, re.IGNORECASE)
                if new_rate_match:
                    interest_rate = self.parse_percentage(new_rate_match.group(1))
            else:
                # Dla innych transakcji szukaj ogólnej stopy
                rate_match = re.search(r'(\d+[,\.]\d+)\s*%', block)
                if rate_match:
                    interest_rate = self.parse_percentage(rate_match.group(1))

            # Połącz odsetki zwykłe i przeterminowane
            total_interest = 0
            if interest_chf:
                total_interest += interest_chf
            if overdue_interest_chf:
                total_interest += overdue_interest_chf

            transaction = {
                'data': parsed_date,
                'typ_operacji': operation_type,
                'kapital_chf': capital_chf,
                'odsetki_chf': total_interest if total_interest > 0 else None,
                'suma_chf': total_chf,
                'kwota_pln': amount_pln,
                'stopa_procentowa': interest_rate,
                'plik_zrodlowy': os.path.basename(pdf_path)
            }

            transactions.append(transaction)
            logger.info(f"Znaleziono transakcję: {parsed_date} - {operation_type}")

        return transactions

    def parse_pdf(self, pdf_path: str) -> List[Dict]:
        """Parsuje pojedynczy PDF"""
        logger.info(f"Przetwarzanie: {pdf_path}")
        pdf_transactions = []

        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    text = page.extract_text()
                    if text:
                        page_transactions = self.extract_from_text(text, pdf_path)
                        pdf_transactions.extend(page_transactions)
                        logger.info(f"  Strona {page_num}: {len(page_transactions)} transakcji")

        except Exception as e:
            logger.error(f"Błąd podczas przetwarzania {pdf_path}: {e}")

        return pdf_transactions

    def parse_multiple_pdfs(self, pdf_paths: List[str]) -> pd.DataFrame:
        """Parsuje wiele PDF-ów i zwraca DataFrame"""
        all_transactions = []

        for pdf_path in pdf_paths:
            transactions = self.parse_pdf(pdf_path)
            all_transactions.extend(transactions)

        # Utwórz DataFrame
        df = pd.DataFrame(all_transactions)

        if df.empty:
            logger.warning("Nie znaleziono żadnych transakcji!")
            return df

        # Usuń duplikaty (ta sama data, typ i kwoty)
        before_count = len(df)
        df = df.drop_duplicates(subset=['data', 'typ_operacji', 'kapital_chf', 'odsetki_chf', 'kwota_pln'])
        after_count = len(df)

        if before_count > after_count:
            logger.info(f"Usunięto {before_count - after_count} duplikatów")

        # Sortuj po dacie (od najstarszych)
        df = df.sort_values('data')

        logger.info(f"Łącznie przetworzono {len(df)} unikalnych transakcji")

        return df


def save_to_files(df: pd.DataFrame, base_filename: str = 'kredyt_chf'):
    """Zapisuje DataFrame do CSV i Excel"""

    if df.empty:
        logger.warning("Brak danych do zapisania!")
        return

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # Zapis do CSV
    csv_filename = f"{base_filename}_{timestamp}.csv"
    df.to_csv(csv_filename, index=False, encoding='utf-8-sig')
    logger.info(f"✓ Zapisano CSV: {csv_filename}")

    # Zapis do Excel z formatowaniem
    excel_filename = f"{base_filename}_{timestamp}.xlsx"
    with pd.ExcelWriter(excel_filename, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Transakcje', index=False)

        # Formatowanie
        worksheet = writer.sheets['Transakcje']

        # Ustaw szerokość kolumn
        column_widths = {
            'A': 12,  # data
            'B': 25,  # typ_operacji
            'C': 12,  # kapital_chf
            'D': 12,  # odsetki_chf
            'E': 12,  # suma_chf
            'F': 12,  # kwota_pln
            'G': 15,  # stopa_procentowa
            'H': 30   # plik_zrodlowy
        }

        for col, width in column_widths.items():
            worksheet.column_dimensions[col].width = width

        # Pogrub nagłówki
        for cell in worksheet[1]:
            cell.font = cell.font.copy(bold=True)

    logger.info(f"✓ Zapisano Excel: {excel_filename}")

    # Opcjonalnie: zapisz również stałą wersję (nadpisywalną)
    csv_latest = f"{base_filename}_latest.csv"
    excel_latest = f"{base_filename}_latest.xlsx"

    df.to_csv(csv_latest, index=False, encoding='utf-8-sig')
    df.to_excel(excel_latest, index=False, engine='openpyxl')

    logger.info(f"✓ Zapisano najnowsze wersje: {csv_latest}, {excel_latest}")


def find_pdf_files(directory: str = '.') -> List[str]:
    """Znajduje wszystkie pliki PDF w katalogu"""
    try:
        # Spróbuj najpierw Path.glob
        pdf_files = list(Path(directory).glob('*.pdf'))
        if not pdf_files:
            # Jeśli nie znaleziono, użyj os.listdir
            import glob
            pattern = os.path.join(directory, '*.pdf')
            pdf_files = [Path(f) for f in glob.glob(pattern)]

        logger.info(f"Znaleziono {len(pdf_files)} plików PDF w {directory}")
        return [str(f) for f in pdf_files]
    except Exception as e:
        logger.error(f"Błąd podczas szukania plików PDF: {e}")
        return []


def main():
    """Główna funkcja programu"""
    # ===== POPRAWKA DLA EXE =====
    # Ustaw kodowanie UTF-8 dla Windows - zabezpieczenie przed None w exe
    if sys.platform == 'win32':
        try:
            import codecs
            # Sprawdź czy stdout/stderr istnieją i mają buffer
            if sys.stdout is not None and hasattr(sys.stdout, 'buffer'):
                sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
            elif sys.stdout is None:
                # W exe bez konsoli - przekieruj do pliku logów
                log_dir = os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else __file__)
                log_file = os.path.join(log_dir, 'app_stdout.log')
                sys.stdout = open(log_file, 'w', encoding='utf-8', buffering=1)

            if sys.stderr is not None and hasattr(sys.stderr, 'buffer'):
                sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
            elif sys.stderr is None:
                # W exe bez konsoli - przekieruj do pliku logów
                log_dir = os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else __file__)
                log_file = os.path.join(log_dir, 'app_stderr.log')
                sys.stderr = open(log_file, 'w', encoding='utf-8', buffering=1)
        except Exception as e:
            # Jeśli coś pójdzie nie tak, stwórz dummy stdout/stderr
            sys.stdout = io.StringIO()
            sys.stderr = io.StringIO()
    # ===== KONIEC POPRAWKI =====

    print("=" * 70)
    print("  KONWERTER PDF -> CSV/EXCEL - Bank Millennium CHF")
    print("=" * 70)
    print()

    # Pobierz katalog z PDF-ami
    if len(sys.argv) > 1:
        pdf_directory = sys.argv[1]
    else:
        pdf_directory = input("Podaj ścieżkę do katalogu z PDF-ami (Enter = bieżący katalog): ").strip()
        if not pdf_directory:
            pdf_directory = '.'

    # Znajdź pliki PDF
    pdf_files = find_pdf_files(pdf_directory)

    if not pdf_files:
        print(f"\n❌ Nie znaleziono plików PDF w katalogu: {pdf_directory}")
        return

    print(f"\n📄 Znalezione pliki PDF:")
    for i, pdf_file in enumerate(pdf_files, 1):
        print(f"  {i}. {os.path.basename(pdf_file)}")

    print(f"\n🔄 Rozpoczynam przetwarzanie {len(pdf_files)} plików...\n")

    # Parsuj PDF-y
    parser = BankMillenniumPDFParser()
    df = parser.parse_multiple_pdfs(pdf_files)

    if df.empty:
        print("\n❌ Nie udało się wyekstrahować żadnych danych z PDF-ów")
        print("   Sprawdź plik pdf_converter.log aby zobaczyć szczegóły")
        return

    # Wyświetl podsumowanie
    print("\n" + "=" * 70)
    print("  PODSUMOWANIE")
    print("=" * 70)
    print(f"  Liczba transakcji: {len(df)}")
    print(f"  Okres: {df['data'].min()} - {df['data'].max()}")
    print(f"  Suma kapitału CHF: {df['kapital_chf'].sum():.2f}" if df['kapital_chf'].notna().any() else "")
    print(f"  Suma odsetek CHF: {df['odsetki_chf'].sum():.2f}" if df['odsetki_chf'].notna().any() else "")
    print(f"  Suma wpłat PLN: {df['kwota_pln'].sum():.2f}" if df['kwota_pln'].notna().any() else "")

    print("\n  Typy operacji:")
    for op_type, count in df['typ_operacji'].value_counts().items():
        print(f"    • {op_type}: {count}")

    print("\n" + "=" * 70)

    # Zapisz do plików
    print("\n💾 Zapisywanie danych...\n")
    save_to_files(df, base_filename='kredyt_chf')

    print("\n" + "=" * 70)
    print("  ✓ ZAKOŃCZONO POMYŚLNIE!")
    print("=" * 70)
    print("\n📊 Możesz teraz otworzyć pliki CSV lub Excel w swojej aplikacji")
    print("📝 Szczegóły przetwarzania znajdziesz w pliku: pdf_converter.log\n")


if __name__ == '__main__':
    main()
