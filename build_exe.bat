@echo off
:: PDF Converter - Build EXE Script
:: No Polish characters for compatibility

echo ================================================================
echo   Build EXE - Bank Millennium CHF PDF Converter
echo ================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found in PATH
    echo Install Python from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [OK] Python found
python --version
echo.

REM Check if pip is installed
pip --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: pip not found
    pause
    exit /b 1
)

echo [OK] pip found
echo.

REM Create virtual environment (optional)
echo [1/5] Creating virtual environment...
if not exist "venv" (
    python -m venv venv
    echo    [OK] Virtual environment created
) else (
    echo    [OK] Virtual environment already exists
)
echo.

REM Activate environment
echo [2/5] Activating virtual environment...
call venv\Scripts\activate.bat
echo    [OK] Environment activated
echo.

REM Install dependencies
echo [3/5] Installing dependencies from requirements.txt...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo    [OK] Dependencies installed
echo.

REM Clean previous builds
echo [4/5] Cleaning previous builds...
if exist "dist" rmdir /s /q dist
if exist "build" rmdir /s /q build
echo    [OK] Cleaned
echo.

REM Build exe
echo [5/5] Building EXE with PyInstaller...
echo    This may take several minutes...
echo.
pyinstaller pdf_converter_gui.spec

if errorlevel 1 (
    echo.
    echo ERROR: Failed to build EXE
    echo Check the logs above
    pause
    exit /b 1
)

echo.
echo ================================================================
echo   BUILD COMPLETED SUCCESSFULLY!
echo ================================================================
echo.
echo EXE file location: dist\PDF_Converter_Millennium_CHF.exe
echo.
echo HOW TO RUN:
echo    1. Go to folder: dist\
echo    2. Run: PDF_Converter_Millennium_CHF.exe
echo    3. Select PDF files to process
echo.
echo NOTE:
echo    - Antivirus may flag the exe as unknown (normal for new exe)
echo    - Add to exceptions if needed
echo.
echo ================================================================
pause
