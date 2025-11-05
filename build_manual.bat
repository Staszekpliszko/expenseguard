@echo off
:: Manual Step-by-Step Build Guide
:: Run each command separately if automatic build fails

echo ================================================================
echo   MANUAL BUILD INSTRUCTIONS
echo ================================================================
echo.
echo If automatic build fails, run these commands manually:
echo.
echo 1. Install PyInstaller:
echo    pip install pyinstaller
echo.
echo 2. Install all dependencies:
echo    pip install pdfplumber pandas openpyxl pillow pypdfium2
echo.
echo 3. Clean old builds:
echo    rmdir /s /q dist
echo    rmdir /s /q build
echo.
echo 4. Build EXE:
echo    pyinstaller pdf_converter_gui.spec
echo.
echo 5. Find your EXE in: dist\PDF_Converter_Millennium_CHF.exe
echo.
echo ================================================================
echo.
echo Press any key to try automatic installation...
pause
echo.

REM Step 1
echo [Step 1/4] Installing PyInstaller...
pip install pyinstaller
echo.

REM Step 2
echo [Step 2/4] Installing dependencies...
pip install pdfplumber pandas openpyxl pillow pypdfium2 pdfminer.six charset-normalizer
echo.

REM Step 3
echo [Step 3/4] Cleaning old builds...
if exist "dist" rmdir /s /q dist
if exist "build" rmdir /s /q build
echo.

REM Step 4
echo [Step 4/4] Building EXE...
pyinstaller pdf_converter_gui.spec
echo.

if exist "dist\PDF_Converter_Millennium_CHF.exe" (
    echo ================================================================
    echo   SUCCESS!
    echo ================================================================
    echo.
    echo Your EXE is ready: dist\PDF_Converter_Millennium_CHF.exe
    echo.
) else (
    echo ================================================================
    echo   BUILD FAILED
    echo ================================================================
    echo.
    echo Please check error messages above.
    echo Try running commands manually (see instructions at the top)
    echo.
)

pause
