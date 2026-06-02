@echo off
title Revethana Assistant - Setup
color 0B

echo.
echo ============================================================
echo   REVETHANA ASSISTANT - Auto Setup Script
echo   Powered by Gemini 2.5 Flash
echo ============================================================
echo.

:: Cek Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python tidak ditemukan!
    echo Download Python 3.9+ dari: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [OK] Python ditemukan:
python --version
echo.

:: Buat virtual environment
echo [1/4] Membuat virtual environment...
python -m venv venv
call venv\Scripts\activate.bat
echo [OK] Virtual environment aktif.
echo.

:: Upgrade pip
echo [2/4] Upgrade pip...
python -m pip install --upgrade pip --quiet
echo [OK] pip diupgrade.
echo.

:: Install dependencies
echo [3/4] Install dependencies...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo [WARN] Beberapa package gagal. Mencoba install PyAudio via pipwin...
    pip install pipwin --quiet
    pipwin install pyaudio
)
echo [OK] Dependencies terinstall.
echo.

:: Cek .env
echo [4/4] Cek konfigurasi .env...
if not exist .env (
    echo [WARN] File .env tidak ditemukan, membuat dari template...
    copy .env.example .env >nul 2>&1
    echo [!] Edit file .env dan masukkan GEMINI_API_KEY kamu!
    echo     Dapatkan gratis di: https://aistudio.google.com/app/apikey
) else (
    echo [OK] File .env ditemukan.
)
echo.

echo ============================================================
echo   Setup selesai!
echo.
echo   Langkah selanjutnya:
echo   1. Edit .env dan isi GEMINI_API_KEY
echo   2. Jalankan: python main.py
echo      atau klik dua kali: run.bat
echo ============================================================
echo.
pause
