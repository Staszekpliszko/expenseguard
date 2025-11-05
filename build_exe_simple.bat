@echo off
chcp 65001 >nul
echo ════════════════════════════════════════════════════════════════
echo   Quick Build EXE (bez venv)
echo ════════════════════════════════════════════════════════════════
echo.

REM Instaluj zależności globalnie
echo [1/3] Instalacja zależności...
pip install -r requirements.txt
echo.

REM Wyczyść poprzednie buildy
echo [2/3] Czyszczenie...
if exist "dist" rmdir /s /q dist
if exist "build" rmdir /s /q build
echo.

REM Build
echo [3/3] Budowanie EXE...
pyinstaller pdf_converter_gui.spec

if errorlevel 1 (
    echo ❌ BŁĄD podczas budowania
    pause
    exit /b 1
)

echo.
echo ✓ GOTOWE! Plik: dist\PDF_Converter_Millennium_CHF.exe
echo.
pause
