#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GUI dla konwertera PDF Bank Millennium CHF do CSV/Excel
Copyright © 2025 A.S. LIVE MEDIA Sp. z O.O.
Developed with Claude AI
Version: 2.0 - Enhanced UI
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
    """Modern GUI for PDF Converter - A.S. LIVE MEDIA"""

    # Color scheme - Professional blue/purple gradient
    COLORS = {
        'primary': '#4A90E2',      # Professional blue
        'secondary': '#667eea',     # Purple-blue
        'accent': '#50C878',        # Emerald green
        'danger': '#E74C3C',        # Red
        'success': '#27ae60',       # Green
        'bg_light': '#F8F9FA',      # Light background
        'bg_dark': '#2C3E50',       # Dark background
        'text_dark': '#2C3E50',     # Dark text
        'text_light': '#FFFFFF',    # White text
        'border': '#E0E0E0'         # Light border
    }

    def __init__(self, root):
        self.root = root
        self.root.title("PDF Converter - Bank Millennium CHF | A.S. LIVE MEDIA")
        self.root.geometry("950x750")
        self.root.resizable(True, True)
        self.root.configure(bg=self.COLORS['bg_light'])

        # ===== POPRAWKA DLA EXE =====
        if sys.platform == 'win32':
            try:
                import codecs
                if sys.stdout is not None and hasattr(sys.stdout, 'buffer'):
                    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
                elif sys.stdout is None:
                    log_dir = os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else __file__)
                    log_file = os.path.join(log_dir, 'app_stdout.log')
                    sys.stdout = open(log_file, 'w', encoding='utf-8', buffering=1)

                if sys.stderr is not None and hasattr(sys.stderr, 'buffer'):
                    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
                elif sys.stderr is None:
                    log_dir = os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else __file__)
                    log_file = os.path.join(log_dir, 'app_stderr.log')
                    sys.stderr = open(log_file, 'w', encoding='utf-8', buffering=1)
            except Exception as e:
                sys.stdout = io.StringIO()
                sys.stderr = io.StringIO()
        # ===== KONIEC POPRAWKI =====

        # Zmienne
        self.pdf_files = []
        self.output_mode = tk.StringVar(value="new")
        self.existing_file = tk.StringVar(value="")
        self.output_folder = tk.StringVar(value=os.getcwd())
        self.parser = BankMillenniumPDFParser()

        # Ustaw styl
        self.setup_style()

        # Utwórz GUI
        self.create_widgets()

    def setup_style(self):
        """Konfiguruje nowoczesny styl dla ttk widgets"""
        style = ttk.Style()
        style.theme_use('clam')

        # Configure Progressbar
        style.configure(
            "Modern.Horizontal.TProgressbar",
            troughcolor=self.COLORS['bg_light'],
            background=self.COLORS['accent'],
            bordercolor=self.COLORS['border'],
            lightcolor=self.COLORS['accent'],
            darkcolor=self.COLORS['accent']
        )

    def create_modern_button(self, parent, text, command, bg_color, width=20):
        """Tworzy nowoczesny przycisk z zaokrąglonymi rogami (symulacja)"""
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            bg=bg_color,
            fg=self.COLORS['text_light'],
            font=("Segoe UI", 10, "bold"),
            padx=20,
            pady=10,
            cursor="hand2",
            relief="flat",
            borderwidth=0,
            activebackground=self._darken_color(bg_color),
            activeforeground=self.COLORS['text_light']
        )
        return btn

    def _darken_color(self, color):
        """Ciemniejszy odcień koloru dla hover effect"""
        # Prosta implementacja - zmniejsz jasność o 20%
        if color.startswith('#'):
            r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
            r, g, b = int(r * 0.8), int(g * 0.8), int(b * 0.8)
            return f'#{r:02x}{g:02x}{b:02x}'
        return color

    def create_widgets(self):
        """Tworzy nowoczesne elementy GUI"""

        # --- HEADER Z GRADIENTEM (symulacja) ---
        header_frame = tk.Frame(self.root, bg=self.COLORS['primary'], height=120)
        header_frame.pack(fill=tk.X, pady=0)
        header_frame.pack_propagate(False)

        # Logo / Title
        title_label = tk.Label(
            header_frame,
            text="📊 PDF CONVERTER PRO",
            font=("Segoe UI", 24, "bold"),
            bg=self.COLORS['primary'],
            fg=self.COLORS['text_light']
        )
        title_label.pack(pady=10)

        subtitle_label = tk.Label(
            header_frame,
            text="Bank Millennium CHF - Professional Loan Analysis Tool",
            font=("Segoe UI", 11),
            bg=self.COLORS['primary'],
            fg=self.COLORS['text_light']
        )
        subtitle_label.pack()

        # Company branding
        company_label = tk.Label(
            header_frame,
            text="© 2025 A.S. LIVE MEDIA Sp. z O.O.",
            font=("Segoe UI", 9),
            bg=self.COLORS['primary'],
            fg=self.COLORS['text_light']
        )
        company_label.pack(pady=(5, 10))

        # --- MAIN CONTAINER ---
        main_frame = tk.Frame(self.root, bg=self.COLORS['bg_light'], padx=30, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- SECTION 1: File Selection ---
        self.create_section_header(main_frame, "1. Select PDF Files")

        button_frame = tk.Frame(main_frame, bg=self.COLORS['bg_light'])
        button_frame.pack(pady=(0, 10))

        self.select_button = self.create_modern_button(
            button_frame,
            "📁 Browse PDF Files",
            self.select_pdfs,
            self.COLORS['primary']
        )
        self.select_button.pack(side=tk.LEFT, padx=5)

        self.clear_button = self.create_modern_button(
            button_frame,
            "🗑️ Clear List",
            self.clear_files,
            self.COLORS['danger'],
            width=15
        )
        self.clear_button.pack(side=tk.LEFT, padx=5)

        # File list with modern styling
        list_container = tk.Frame(main_frame, bg=self.COLORS['border'], padx=1, pady=1)
        list_container.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        list_frame = tk.Frame(list_container, bg=self.COLORS['text_light'])
        list_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.file_listbox = tk.Listbox(
            list_frame,
            height=8,
            yscrollcommand=scrollbar.set,
            font=("Consolas", 9),
            selectmode=tk.EXTENDED,
            bg=self.COLORS['text_light'],
            fg=self.COLORS['text_dark'],
            selectbackground=self.COLORS['primary'],
            selectforeground=self.COLORS['text_light'],
            borderwidth=0,
            highlightthickness=0
        )
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.config(command=self.file_listbox.yview)

        # --- SECTION 2: Output Mode ---
        self.create_section_header(main_frame, "2. Select Output Mode")

        mode_frame = tk.Frame(main_frame, bg=self.COLORS['bg_light'])
        mode_frame.pack(pady=(0, 10))

        self.new_file_radio = tk.Radiobutton(
            mode_frame,
            text="📄 Create New File",
            variable=self.output_mode,
            value="new",
            font=("Segoe UI", 10),
            bg=self.COLORS['bg_light'],
            fg=self.COLORS['text_dark'],
            selectcolor=self.COLORS['bg_light'],
            activebackground=self.COLORS['bg_light'],
            command=self.toggle_append_mode
        )
        self.new_file_radio.pack(anchor=tk.W, pady=2)

        self.append_file_radio = tk.Radiobutton(
            mode_frame,
            text="➕ Append to Existing File (CSV or Excel)",
            variable=self.output_mode,
            value="append",
            font=("Segoe UI", 10),
            bg=self.COLORS['bg_light'],
            fg=self.COLORS['text_dark'],
            selectcolor=self.COLORS['bg_light'],
            activebackground=self.COLORS['bg_light'],
            command=self.toggle_append_mode
        )
        self.append_file_radio.pack(anchor=tk.W, pady=2)

        # Existing file selection
        append_frame = tk.Frame(main_frame, bg=self.COLORS['bg_light'])
        append_frame.pack(fill=tk.X, pady=(0, 15))

        self.existing_file_entry = tk.Entry(
            append_frame,
            textvariable=self.existing_file,
            state="disabled",
            font=("Segoe UI", 9),
            bg=self.COLORS['text_light'],
            fg=self.COLORS['text_dark'],
            disabledbackground='#E8E8E8',
            disabledforeground='#999999'
        )
        self.existing_file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(30, 5))

        self.browse_button = self.create_modern_button(
            append_frame,
            "Browse...",
            self.browse_existing_file,
            self.COLORS['secondary'],
            width=12
        )
        self.browse_button.pack(side=tk.LEFT)
        self.browse_button.config(state="disabled")

        # --- SECTION 3: Output Folder ---
        self.create_section_header(main_frame, "3. Select Output Folder")

        output_frame = tk.Frame(main_frame, bg=self.COLORS['bg_light'])
        output_frame.pack(fill=tk.X, pady=(0, 15))

        self.output_folder_entry = tk.Entry(
            output_frame,
            textvariable=self.output_folder,
            font=("Segoe UI", 9),
            bg=self.COLORS['text_light'],
            fg=self.COLORS['text_dark']
        )
        self.output_folder_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        self.browse_folder_button = self.create_modern_button(
            output_frame,
            "📁 Browse...",
            self.browse_output_folder,
            self.COLORS['secondary'],
            width=12
        )
        self.browse_folder_button.pack(side=tk.LEFT)

        # --- SECTION 4: Process ---
        self.create_section_header(main_frame, "4. Convert PDFs")

        self.process_button = self.create_modern_button(
            main_frame,
            "🚀 START CONVERSION",
            self.process_files,
            self.COLORS['success']
        )
        self.process_button.pack(pady=(0, 15))

        # Modern Progress Bar
        self.progress = ttk.Progressbar(
            main_frame,
            mode='indeterminate',
            length=500,
            style="Modern.Horizontal.TProgressbar"
        )
        self.progress.pack(pady=(0, 10))

        # Status
        self.status_label = tk.Label(
            main_frame,
            text="✓ Ready to process files",
            font=("Segoe UI", 10),
            fg=self.COLORS['text_dark'],
            bg=self.COLORS['bg_light']
        )
        self.status_label.pack()

        # --- FOOTER ---
        footer_frame = tk.Frame(self.root, bg=self.COLORS['bg_dark'], height=40)
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM)
        footer_frame.pack_propagate(False)

        footer_text = tk.Label(
            footer_frame,
            text="Powered by A.S. LIVE MEDIA Sp. z O.O. | Developed with Claude AI | v2.0",
            font=("Segoe UI", 8),
            bg=self.COLORS['bg_dark'],
            fg=self.COLORS['text_light']
        )
        footer_text.pack(pady=12)

        # Grid configuration
        main_frame.columnconfigure(0, weight=1)

    def create_section_header(self, parent, text):
        """Tworzy nagłówek sekcji"""
        label = tk.Label(
            parent,
            text=text,
            font=("Segoe UI", 12, "bold"),
            fg=self.COLORS['text_dark'],
            bg=self.COLORS['bg_light'],
            anchor="w"
        )
        label.pack(fill=tk.X, pady=(10, 5))

        # Separator line
        separator = tk.Frame(parent, height=2, bg=self.COLORS['primary'])
        separator.pack(fill=tk.X, pady=(0, 10))

    def select_pdfs(self):
        """Wybiera pliki PDF"""
        files = filedialog.askopenfilenames(
            title="Select PDF Files",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )

        if files:
            for file in files:
                if file not in self.pdf_files:
                    self.pdf_files.append(file)
                    self.file_listbox.insert(tk.END, os.path.basename(file))

            self.update_status(f"✓ Selected {len(self.pdf_files)} files", self.COLORS['success'])

    def clear_files(self):
        """Czyści listę plików"""
        self.pdf_files = []
        self.file_listbox.delete(0, tk.END)
        self.update_status("✓ File list cleared", self.COLORS['text_dark'])

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
            title="Select Existing CSV or Excel File",
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
            title="Select Output Folder",
            initialdir=self.output_folder.get()
        )

        if folder:
            self.output_folder.set(folder)

    def update_status(self, message, color=None):
        """Aktualizuje status z kolorem"""
        self.status_label.config(text=message)
        if color:
            self.status_label.config(fg=color)
        self.root.update_idletasks()

    def process_files(self):
        """Przetwarza pliki PDF"""
        if not self.pdf_files:
            messagebox.showwarning(
                "No Files",
                "Please select PDF files to process first!"
            )
            return

        if self.output_mode.get() == "append" and not self.existing_file.get():
            messagebox.showwarning(
                "No Target File",
                "Please select an existing CSV/Excel file to append to!"
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

            self.update_status("⏳ Processing PDFs...", self.COLORS['secondary'])

            # Parsuj wszystkie PDF-y
            df = self.parser.parse_multiple_pdfs(self.pdf_files)

            if df.empty:
                self.root.after(0, lambda: messagebox.showerror(
                    "Error",
                    "Failed to extract any data from PDFs!\nCheck pdf_converter.log"
                ))
                return

            self.update_status("💾 Saving data...", self.COLORS['secondary'])

            # Zapisz dane
            if self.output_mode.get() == "append":
                self.append_to_existing(df)
            else:
                self.save_new_files(df)

            # Pokaż podsumowanie
            summary = self.create_summary(df)
            self.root.after(0, lambda: messagebox.showinfo(
                "Success! ✓",
                summary
            ))

            self.update_status(f"✓ Completed! Processed {len(df)} transactions", self.COLORS['success'])

        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror(
                "Error",
                f"An error occurred during processing:\n{str(e)}"
            ))
            self.update_status("❌ Error during processing", self.COLORS['danger'])

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
            self.update_status(f"Added {len(new_df)} new, removed {duplicates_removed} duplicates")

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
            df.to_excel(writer, sheet_name='Transactions', index=False)

        # Latest versions
        latest_csv = os.path.join(output_dir, "kredyt_chf_latest.csv")
        latest_xlsx = os.path.join(output_dir, "kredyt_chf_latest.xlsx")
        df.to_csv(latest_csv, index=False, encoding='utf-8-sig')
        df.to_excel(latest_xlsx, index=False, engine='openpyxl')

    def create_summary(self, df):
        """Tworzy podsumowanie wyników"""
        summary = f"""
Processing completed successfully!

📊 STATISTICS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Number of transactions: {len(df)}
• Period: {df['data'].min()} - {df['data'].max()}
"""

        if df['kapital_chf'].notna().any():
            summary += f"• Total capital CHF: {df['kapital_chf'].sum():.2f}\n"

        if df['odsetki_chf'].notna().any():
            summary += f"• Total interest CHF: {df['odsetki_chf'].sum():.2f}\n"

        if df['kwota_pln'].notna().any():
            summary += f"• Total payments PLN: {df['kwota_pln'].sum():.2f}\n"

        summary += "\n📁 OPERATION TYPES:\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        for op_type, count in df['typ_operacji'].value_counts().items():
            summary += f"• {op_type}: {count}\n"

        summary += "\n© A.S. LIVE MEDIA Sp. z O.O."

        return summary


def main():
    """Główna funkcja GUI"""
    root = tk.Tk()
    app = PDFConverterGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
