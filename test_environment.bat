@echo off
:: Test if environment is ready for building EXE

echo ================================================================
echo   ENVIRONMENT TEST
echo ================================================================
echo.

echo Testing Python installation...
python --version
if errorlevel 1 (
    echo [FAIL] Python not found!
    echo.
    echo SOLUTION:
    echo 1. Install Python from: https://www.python.org/downloads/
    echo 2. During installation CHECK: "Add Python to PATH"
    echo 3. Restart computer
    echo 4. Run this test again
    echo.
    pause
    exit /b 1
) else (
    echo [OK] Python is installed
)
echo.

echo Testing pip...
pip --version
if errorlevel 1 (
    echo [FAIL] pip not found!
    echo.
    echo SOLUTION:
    echo Run: python -m ensurepip --upgrade
    echo.
    pause
    exit /b 1
) else (
    echo [OK] pip is installed
)
echo.

echo Testing PyInstaller...
pyinstaller --version >nul 2>&1
if errorlevel 1 (
    echo [WARN] PyInstaller not installed
    echo.
    echo Run: pip install pyinstaller
    echo.
) else (
    pyinstaller --version
    echo [OK] PyInstaller is installed
)
echo.

echo Testing required files...
if not exist "pdf_converter_gui.py" (
    echo [FAIL] pdf_converter_gui.py not found!
    goto :missing_files
)
echo [OK] pdf_converter_gui.py found

if not exist "pdf_to_csv.py" (
    echo [FAIL] pdf_to_csv.py not found!
    goto :missing_files
)
echo [OK] pdf_to_csv.py found

if not exist "pdf_converter_gui.spec" (
    echo [FAIL] pdf_converter_gui.spec not found!
    goto :missing_files
)
echo [OK] pdf_converter_gui.spec found

if not exist "requirements.txt" (
    echo [FAIL] requirements.txt not found!
    goto :missing_files
)
echo [OK] requirements.txt found

echo.
echo ================================================================
echo   ALL TESTS PASSED!
echo ================================================================
echo.
echo Your environment is ready to build EXE.
echo Run: build_exe_simple.bat
echo.
pause
exit /b 0

:missing_files
echo.
echo ================================================================
echo   MISSING FILES!
echo ================================================================
echo.
echo Make sure you copied all files to this folder:
echo - pdf_converter_gui.py
echo - pdf_to_csv.py
echo - pdf_converter_gui.spec
echo - requirements.txt
echo - build_exe.bat
echo - build_exe_simple.bat
echo.
pause
exit /b 1
