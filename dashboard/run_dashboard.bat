@echo off
REM ─────────────────────────────────────────────────────────────────────────
REM  Ghana ANC Fertility Dashboard — Windows Launcher (.bat)
REM  Double-click this file to launch the dashboard.
REM ─────────────────────────────────────────────────────────────────────────

cd /d "%~dp0"

echo ==================================================
echo   Ghana ANC Fertility Spatial Analysis Dashboard
echo ==================================================
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found.
    echo Please install Python 3 from https://python.org
    pause
    exit /b 1
)

REM Install dependencies if needed
echo Checking dependencies...
python -c "import dash, dash_bootstrap_components, plotly, pandas" 2>nul
if %errorlevel% neq 0 (
    echo Installing required packages...
    pip install dash dash-bootstrap-components plotly pandas numpy scipy --quiet
)

echo Starting dashboard at http://127.0.0.1:8050
timeout /t 2 /nobreak >nul
start "" "http://127.0.0.1:8050"

python app.py
pause
