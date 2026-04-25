@echo off
chcp 65001 >nul
echo ====================================
echo healthy_pet
echo ====================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo Python 3.9 or newer is required.
    pause
    exit /b 1
)

python run.py

if errorlevel 1 (
    echo.
    echo Failed to start healthy_pet.
    pause
)
