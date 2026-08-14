@echo off
setlocal
title Setup Python

echo ========================================
echo        SETUP PROGETTO PYTHON
echo ========================================
echo.

:: Controlla Python
echo [1/4] Controllo Python...

where python >nul 2>&1

if %errorlevel% neq 0 (
    echo.
    echo [ERRORE] Python non e' installato oppure non e' presente nel PATH.
    echo.
    echo Installa Python da:
    echo https://www.python.org/downloads/windows/
    echo.
    pause
    exit /b 1
)

python --version
if %errorlevel% neq 0 (
    echo [ERRORE] Python non funziona correttamente.
    pause
    exit /b 1
)

echo Python trovato!
echo.

:: Controlla pip
echo [2/4] Controllo pip...

python -m pip --version >nul 2>&1

if %errorlevel% neq 0 (
    echo [ERRORE] pip non e' disponibile.
    echo Provo a installarlo...
    
    python -m ensurepip --upgrade
    
    if %errorlevel% neq 0 (
        echo [ERRORE] Impossibile installare pip.
        pause
        exit /b 1
    )
)

echo pip trovato!
echo.

:: Crea ambiente virtuale
echo [3/4] Creazione ambiente virtuale...

if not exist ".venv" (
    python -m venv .venv
    
    if %errorlevel% neq 0 (
        echo [ERRORE] Impossibile creare il virtual environment.
        pause
        exit /b 1
    )
    
    echo Ambiente virtuale creato!
) else (
    echo Ambiente virtuale gia' presente.
)

echo.

:: Installa requests
echo [4/4] Installazione dipendenze...

call .venv\Scripts\activate.bat

python -m pip install --upgrade pip
python -m pip install requests

if %errorlevel% neq 0 (
    echo.
    echo [ERRORE] Installazione di requests fallita.
    pause
    exit /b 1
)

echo.
echo ========================================
echo          INSTALLAZIONE COMPLETATA
echo ========================================
echo.
echo Python:
python --version
echo.
echo requests:
python -m pip show requests | findstr "Name Version"
echo.

:: Avvia il programma
if exist "main.py" (
    echo Avvio main.py...
    echo.
    python main.py
) else (
    echo main.py non trovato.
    echo Metti questo file .bat nella cartella del progetto.
)

echo.
pause