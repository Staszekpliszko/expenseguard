@echo off
chcp 65001 >nul
echo ════════════════════════════════════════════════════════════════
echo   Build EXE - Konwerter PDF Bank Millennium CHF
echo ════════════════════════════════════════════════════════════════
echo.

REM Sprawdź czy Python jest zainstalowany
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ BŁĄD: Python nie jest zainstalowany lub nie jest w PATH
    echo    Zainstaluj Python z: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✓ Python znaleziony
python --version
echo.

REM Sprawdź czy pip jest zainstalowany
pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ BŁĄD: pip nie jest zainstalowany
    pause
    exit /b 1
)

echo ✓ pip znaleziony
echo.

REM Utwórz środowisko wirtualne (opcjonalnie)
echo [1/5] Tworzenie środowiska wirtualnego...
if not exist "venv" (
    python -m venv venv
    echo    ✓ Środowisko utworzone
) else (
    echo    ✓ Środowisko już istnieje
)
echo.

REM Aktywuj środowisko
echo [2/5] Aktywacja środowiska wirtualnego...
call venv\Scripts\activate.bat
echo    ✓ Środowisko aktywne
echo.

REM Zainstaluj zależności
echo [3/5] Instalacja zależności z requirements.txt...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ BŁĄD: Nie udało się zainstalować zależności
    pause
    exit /b 1
)
echo    ✓ Zależności zainstalowane
echo.

REM Wyczyść poprzednie buildy
echo [4/5] Czyszczenie poprzednich buildów...
if exist "dist" rmdir /s /q dist
if exist "build" rmdir /s /q build
echo    ✓ Wyczyszczono
echo.

REM Build exe
echo [5/5] Budowanie EXE z PyInstaller...
echo    To może potrwać kilka minut...
echo.
pyinstaller pdf_converter_gui.spec

if errorlevel 1 (
    echo.
    echo ❌ BŁĄD: Nie udało się zbudować EXE
    echo    Sprawdź logi powyżej
    pause
    exit /b 1
)

echo.
echo ════════════════════════════════════════════════════════════════
echo   ✓ BUILD ZAKOŃCZONY POMYŚLNIE!
echo ════════════════════════════════════════════════════════════════
echo.
echo 📁 Plik EXE znajduje się w: dist\PDF_Converter_Millennium_CHF.exe
echo.
echo 🚀 URUCHOMIENIE:
echo    1. Przejdź do folderu: dist\
echo    2. Uruchom: PDF_Converter_Millennium_CHF.exe
echo    3. Wybierz PDF-y do przetworzenia
echo.
echo 💡 UWAGA:
echo    - Program może być oznaczony przez antywirus jako nieznany
echo    - To normalne dla nowo zbudowanych exe
echo    - Dodaj do wyjątków jeśli potrzeba
echo.
echo ════════════════════════════════════════════════════════════════
pause
