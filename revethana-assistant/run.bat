@echo off
title Revethana Assistant
color 0B

:: Aktifkan venv jika ada
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

:: Jalankan assistant
python main.py

:: Jika error, pause agar user bisa baca error message
if errorlevel 1 (
    echo.
    echo [ERROR] Revethana berhenti karena error.
    echo Cek pesan error di atas.
    pause
)
