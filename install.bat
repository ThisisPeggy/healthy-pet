@echo off
chcp 65001 >nul
echo ====================================
echo Install healthy_pet Dependencies
echo ====================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo Python 3.9 or newer is required.
    pause
    exit /b 1
)

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo Failed to install dependencies.
    pause
    exit /b 1
)

echo.
echo Dependencies installed.
pause
