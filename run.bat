@echo off
chcp 65001 >nul

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo.
    echo [ERROR] Virtual environment not found!
    echo Please run setup.bat first to create the environment.
    echo.
    pause
    exit /b 1
)

REM Activate virtual environment and run app
call venv\Scripts\activate.bat
echo.
echo [INFO] Running in virtual environment: %VIRTUAL_ENV%
echo [INFO] Python location:
where python
echo.
python app.py

REM Keep window open if app exits with error
if errorlevel 1 (
    echo.
    echo [ERROR] App exited with error code: %errorlevel%
    pause
)
