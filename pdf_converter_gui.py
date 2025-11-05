#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GUI dla konwertera PDF Bank Millennium CHF do CSV/Excel
Autor: Claude
Data: 2025-11-04
Poprawki: 2025-11-05 - Fix dla kompilacji do exe
"""

import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
import pandas as pd
from datetime import datetime
import threading
import io

# Import z głównego skryptu
from pdf_to_csv import BankMillenniumPDFParser


class PDFConverterGUI:
    """GUI dla konwertera PDF"""

    def __init__(self, root):
        self.root = root
        self.root.title("Konwerter PDF -> CSV/Excel - Bank Millennium CHF")
        self.root.geometry("900x700")
        self.root.resizable(True, True)

        # ===== POPRAWKA DLA EXE =====
        # Ustaw kodowanie dla Windows - zabezpieczenie przed None w exe
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

        # Zmienne
        self.pdf_files = []
        self.output_mode = tk.StringVar(value="new")  # "new" lub "append"
        self.existing_file = tk.StringVar(value="")
        self.output_folder = tk.StringVar(value=os.getcwd())  # Folder wyjściowy
        self.parser = BankMillenniumPDFParser()

        # Utwórz GUI
        self.create_widgets()

    def create_widgets(self):
        """Tworzy elementy GUI"""

        # --- NAGŁÓWEK ---
        header_frame = tk.Frame(self.root, bg="#667eea", height=80)
        header_frame.pack(fill=tk.X, pady=0)
        header_frame.pack_propagate(False)

        title_label = tk.Label(
            header_frame,
            text="📊 Konwerter PDF -> CSV/Excel",
            font=("Arial", 20, "bold"),
            bg="#667eea",
            fg="white"
        )
        title_label.pack(pady=10)

        subtitle_label = tk.Label(
            header_frame,
            text="Bank Millennium CHF - Analiza Spłat Kredytu",
            font=("Arial", 11),
            bg="#667eea",
            fg="white"
        )
        subtitle_label.pack()

        # --- GŁÓWNY KONTENER ---
        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- SEKCJA 1: Wybór plików PDF ---
        files_label = tk.Label(
            main_frame,
            text="1. Wybierz pliki PDF:",
            font=("Arial", 12, "bold")
        )
        files_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))

        button_frame = tk.Frame(main_frame)
        button_frame.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))

        self.select_button = tk.Button(
            button_frame,
            text="📁 Wybierz PDF-y",
            command=self.select_pdfs,
            bg="#667eea",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=15,
            pady=8,
            cursor="hand2"
        )
        self.select_button.pack(side=tk.LEFT, padx=(0, 10))

        self.clear_button = tk.Button(
            button_frame,
            text="🗑️ Wyczyść listę",
            command=self.clear_files,
            bg="#e74c3c",
            fg="white",
            font=("Arial", 10),
            padx=15,
            pady=8,
            cursor="hand2"
        )
        self.clear_button.pack(side=tk.LEFT)

        # Lista plików
        list_frame = tk.Frame(main_frame)
        list_frame.grid(row=2, column=0, columnspan=2, sticky=tk.NSEW, pady=(0, 15))

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.file_listbox = tk.Listbox(
            list_frame,
            height=8,
            yscrollcommand=scrollbar.set,
            font=("Courier", 9),
            selectmode=tk.EXTENDED
        )
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.file_listbox.yview)

        # --- SEKCJA 2: Tryb zapisu ---
        mode_label = tk.Label(
            main_frame,
            text="2. Wybierz tryb zapisu:",
            font=("Arial", 12, "bold")
        )
        mode_label.grid(row=3, column=0, sticky=tk.W, pady=(10, 5))

        mode_frame = tk.Frame(main_frame)
        mode_frame.grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))

        self.new_file_radio = tk.Radiobutton(
            mode_frame,
            text="📄 Utwórz nowy plik",
            variable=self.output_mode,
            value="new",
            font=("Arial", 10),
            command=self.toggle_append_mode
        )
        self.new_file_radio.pack(anchor=tk.W, pady=2)

        self.append_file_radio = tk.Radiobutton(
            mode_frame,
            text="➕ Dopisz do istniejącego pliku (CSV lub Excel)",
            variable=self.output_mode,
            value="append",
            font=("Arial", 10),
            command=self.toggle_append_mode
        )
        self.append_file_radio.pack(anchor=tk.W, pady=2)

        # Wybór istniejącego pliku
        append_frame = tk.Frame(main_frame)
        append_frame.grid(row=5, column=0, columnspan=2, sticky=tk.EW, pady=(0, 15))

        self.existing_file_entry = tk.Entry(
            append_frame,
            textvariable=self.existing_file,
            state="disabled",
            font=("Arial", 9),
            width=60
        )
        self.existing_file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(20, 5))

        self.browse_button = tk.Button(
            append_frame,
            text="Przeglądaj...",
            command=self.browse_existing_file,
            state="disabled",
            font=("Arial", 9),
            padx=10,
            pady=5
        )
        self.browse_button.pack(side=tk.LEFT)

        # --- SEKCJA 3: Folder wyjściowy ---
        output_label = tk.Label(
            main_frame,
            text="3. Wybierz folder zapisu:",
            font=("Arial", 12, "bold")
        )
        output_label.grid(row=6, column=0, sticky=tk.W, pady=(10, 5))

        output_frame = tk.Frame(main_frame)
        output_frame.grid(row=7, column=0, columnspan=2, sticky=tk.EW, pady=(0, 15))

        self.output_folder_entry = tk.Entry(
            output_frame,
            textvariable=self.output_folder,
            font=("Arial", 9),
            width=60
        )
        self.output_folder_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        self.browse_folder_button = tk.Button(
            output_frame,
            text="Wybierz folder...",
            command=self.browse_output_folder,
            font=("Arial", 9),
            padx=10,
            pady=5
        )
        self.browse_folder_button.pack(side=tk.LEFT)

        # --- SEKCJA 4: Przetwarzanie ---
        process_label = tk.Label(
            main_frame,
            text="4. Przetwórz pliki:",
            font=("Arial", 12, "bold")
        )
        process_label.grid(row=8, column=0, sticky=tk.W, pady=(10, 5))

        self.process_button = tk.Button(
            main_frame,
            text="🚀 Rozpocznij konwersję",
            command=self.process_files,
            bg="#27ae60",
            fg="white",
            font=("Arial", 12, "bold"),
            padx=20,
            pady=12,
            cursor="hand2"
        )
        self.process_button.grid(row=9, column=0, columnspan=2, pady=(0, 15))

        # Pasek postępu
        self.progress = ttk.Progressbar(
            main_frame,
            mode='indeterminate',
            length=400
        )
        self.progress.grid(row=10, column=0, columnspan=2, pady=(0, 10))

        # Status
        self.status_label = tk.Label(
            main_frame,
            text="Gotowy do pracy",
            font=("Arial", 10),
            fg="#666"
        )
        self.status_label.grid(row=11, column=0, columnspan=2)

        # Konfiguracja grid
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)

    def select_pdfs(self):
        """Wybiera pliki PDF"""
        files = filedialog.askopenfilenames(
            title="Wybierz pliki PDF",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )

        if files:
            for file in files:
                if file not in self.pdf_files:
                    self.pdf_files.append(file)
                    self.file_listbox.insert(tk.END, os.path.basename(file))

            self.update_status(f"Wybrano {len(self.pdf_files)} plików")

    def clear_files(self):
        """Czyści listę plików"""
        self.pdf_files = []
        self.file_listbox.delete(0, tk.END)
        self.update_status("Lista plików wyczyszczona")

    def toggle_append_mode(self):
        """Przełącza tryb dopisywania"""
        if self.output_mode.get() == "append":
            self.existing_file_entry.config(state="normal")
            self.browse_button.config(state="normal")
        else:
            self.existing_file_entry.config(state="disabled")
            self.browse_button.config(state="disabled")

    def browse_existing_file(self):
        """Wybiera istniejący plik CSV/Excel"""
        file = filedialog.askopenfilename(
            title="Wybierz istniejący plik CSV lub Excel",
            filetypes=[
                ("CSV files", "*.csv"),
                ("Excel files", "*.xlsx"),
                ("All files", "*.*")
            ]
        )

        if file:
            self.existing_file.set(file)

    def browse_output_folder(self):
        """Wybiera folder wyjściowy"""
        folder = filedialog.askdirectory(
            title="Wybierz folder zapisu plików CSV/Excel",
            initialdir=self.output_folder.get()
        )

        if folder:
            self.output_folder.set(folder)

    def update_status(self, message):
        """Aktualizuje status"""
        self.status_label.config(text=message)
        self.root.update_idletasks()

    def process_files(self):
        """Przetwarza pliki PDF"""
        if not self.pdf_files:
            messagebox.showwarning(
                "Brak plików",
                "Najpierw wybierz pliki PDF do przetworzenia!"
            )
            return

        if self.output_mode.get() == "append" and not self.existing_file.get():
            messagebox.showwarning(
                "Brak pliku docelowego",
                "Wybierz istniejący plik CSV/Excel do którego chcesz dopisać dane!"
            )
            return

        # Uruchom przetwarzanie w osobnym wątku
        thread = threading.Thread(target=self._process_thread)
        thread.daemon = True
        thread.start()

    def _process_thread(self):
        """Wątek przetwarzania"""
        try:
            self.process_button.config(state="disabled")
            self.select_button.config(state="disabled")
            self.progress.start()

            self.update_status("Przetwarzanie PDF-ów...")

            # Parsuj wszystkie PDF-y
            df = self.parser.parse_multiple_pdfs(self.pdf_files)

            if df.empty:
                self.root.after(0, lambda: messagebox.showerror(
                    "Błąd",
                    "Nie udało się wyekstrahować żadnych danych z PDF-ów!\n"
                    "Sprawdź plik pdf_converter.log"
                ))
                return

            self.update_status("Zapisywanie danych...")

            # Zapisz dane
            if self.output_mode.get() == "append":
                self.append_to_existing(df)
            else:
                self.save_new_files(df)

            # Pokaż podsumowanie
            summary = self.create_summary(df)
            self.root.after(0, lambda: messagebox.showinfo(
                "Sukces! ✓",
                summary
            ))

            self.update_status(f"Zakończono! Przetworzono {len(df)} transakcji")

        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror(
                "Błąd",
                f"Wystąpił błąd podczas przetwarzania:\n{str(e)}"
            ))
            self.update_status("Błąd podczas przetwarzania")

        finally:
            self.progress.stop()
            self.process_button.config(state="normal")
            self.select_button.config(state="normal")

    def append_to_existing(self, new_df):
        """Dopisuje dane do istniejącego pliku"""
        existing_path = self.existing_file.get()

        # Wczytaj istniejące dane
        if existing_path.endswith('.csv'):
            existing_df = pd.read_csv(existing_path, encoding='utf-8-sig')
        else:
            existing_df = pd.read_excel(existing_path)

        # Połącz dane
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)

        # Usuń duplikaty
        before_count = len(combined_df)
        combined_df = combined_df.drop_duplicates(
            subset=['data', 'typ_operacji', 'kapital_chf', 'odsetki_chf', 'kwota_pln']
        )
        after_count = len(combined_df)

        duplicates_removed = before_count - after_count

        # Sortuj po dacie
        combined_df = combined_df.sort_values('data')

        # Zapisz
        if existing_path.endswith('.csv'):
            combined_df.to_csv(existing_path, index=False, encoding='utf-8-sig')
        else:
            combined_df.to_excel(existing_path, index=False, engine='openpyxl')

        if duplicates_removed > 0:
            self.update_status(f"Dodano {len(new_df)} nowych, usunięto {duplicates_removed} duplikatów")

    def save_new_files(self, df):
        """Zapisuje nowe pliki CSV i Excel"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_dir = self.output_folder.get()

        # CSV
        csv_filename = os.path.join(output_dir, f"kredyt_chf_{timestamp}.csv")
        df.to_csv(csv_filename, index=False, encoding='utf-8-sig')

        # Excel
        excel_filename = os.path.join(output_dir, f"kredyt_chf_{timestamp}.xlsx")
        with pd.ExcelWriter(excel_filename, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Transakcje', index=False)

        # Nadpisywalne wersje
        latest_csv = os.path.join(output_dir, "kredyt_chf_latest.csv")
        latest_xlsx = os.path.join(output_dir, "kredyt_chf_latest.xlsx")
        df.to_csv(latest_csv, index=False, encoding='utf-8-sig')
        df.to_excel(latest_xlsx, index=False, engine='openpyxl')

    def create_summary(self, df):
        """Tworzy podsumowanie wyników"""
        summary = f"""
Przetwarzanie zakończone pomyślnie!

📊 STATYSTYKI:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Liczba transakcji: {len(df)}
• Okres: {df['data'].min()} - {df['data'].max()}
"""

        if df['kapital_chf'].notna().any():
            summary += f"• Suma kapitału CHF: {df['kapital_chf'].sum():.2f}\n"

        if df['odsetki_chf'].notna().any():
            summary += f"• Suma odsetek CHF: {df['odsetki_chf'].sum():.2f}\n"

        if df['kwota_pln'].notna().any():
            summary += f"• Suma wpłat PLN: {df['kwota_pln'].sum():.2f}\n"

        summary += "\n📁 TYPY OPERACJI:\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        for op_type, count in df['typ_operacji'].value_counts().items():
            summary += f"• {op_type}: {count}\n"

        return summary


def main():
    """Główna funkcja GUI"""
    root = tk.Tk()
    app = PDFConverterGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
