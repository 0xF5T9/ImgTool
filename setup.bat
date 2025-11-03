@echo off
echo.
echo ============================================================
echo        ImgTool - Setup and Installation
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found! Please install Python first.
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/4] Checking Python version...
python --version

echo.
echo [2/4] Creating virtual environment...
if exist "venv" (
    echo Virtual environment already exists, skipping creation...
) else (
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment!
        pause
        exit /b 1
    )
    echo Virtual environment created successfully!
)

echo.
echo [3/4] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment!
    pause
    exit /b 1
)

echo.
echo [4/4] Installing dependencies...
echo Installing: Pillow, prompt-toolkit, pygments, rich
pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies!
    pause
    exit /b 1
)

echo.
echo ============================================================
echo Setup completed successfully!
echo ============================================================
echo.
echo Next steps:
echo   1. Run: run.bat
echo   2. Or manually: venv\Scripts\activate.bat then python app.py
echo.
pause
