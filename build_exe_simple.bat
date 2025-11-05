@echo off
:: Quick Build EXE (without virtualenv)
:: No Polish characters for compatibility

echo ================================================================
echo   Quick Build EXE (no venv)
echo ================================================================
echo.

REM Install dependencies globally
echo [1/3] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo.

REM Clean previous builds
echo [2/3] Cleaning previous builds...
if exist "dist" rmdir /s /q dist
if exist "build" rmdir /s /q build
echo.

REM Build
echo [3/3] Building EXE...
pyinstaller pdf_converter_gui.spec

if errorlevel 1 (
    echo ERROR: Build failed
    pause
    exit /b 1
)

echo.
echo ================================================================
echo   SUCCESS! File: dist\PDF_Converter_Millennium_CHF.exe
echo ================================================================
echo.
pause
