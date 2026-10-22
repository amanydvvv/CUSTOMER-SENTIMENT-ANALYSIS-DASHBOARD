@echo off
title Customer Feedback Intelligence — Launcher
color 0A

:: ─────────────────────────────────────────────────────────────────────────────
:: PROJECT PYTHON: C:\Program Files\Python310\python.exe
:: All project dependencies (fastapi, streamlit, torch, etc.) are installed here.
:: This launcher BYPASSES the system PATH so Python 3.13/3.14 is never picked up.
:: ─────────────────────────────────────────────────────────────────────────────

set PYTHON=C:\Program Files\Python310\python.exe
set PROJECT_DIR=%~dp0

echo ============================================================
echo   Customer Feedback Intelligence Dashboard
echo   Backend  : http://localhost:8000/docs
echo   Frontend : http://localhost:8501
echo ============================================================
echo.

:: Step 1 — Verify correct Python
echo [CHECK] Using Python:
"%PYTHON%" --version
echo.

:: Step 2 — Seed database (idempotent)
echo [1/3] Initialising database schema...
"%PYTHON%" "%PROJECT_DIR%backend\init_db.py"
echo.

:: Step 3 — Start FastAPI backend in its own window
echo [2/3] Launching FastAPI backend on port 8000...
start "FastAPI Backend :8000" cmd /k "cd /d "%PROJECT_DIR%backend" && "C:\Program Files\Python310\python.exe" -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

:: Give backend 3 s to bind
timeout /t 3 /nobreak >nul

:: Step 4 — Start Streamlit frontend in its own window
echo [3/3] Launching Streamlit frontend on port 8501...
start "Streamlit Dashboard :8501" cmd /k ""C:\Program Files\Python310\python.exe" -m streamlit run "%PROJECT_DIR%frontend\streamlit_app.py" --server.port 8501"

echo.
echo ============================================================
echo   Both services started in separate windows.
echo   Close those windows to stop the services.
echo ============================================================
echo.
pause
