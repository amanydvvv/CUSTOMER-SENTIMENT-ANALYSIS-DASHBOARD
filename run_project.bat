@echo off
title Customer Feedback Intelligence Launcher
color 0A

echo ========================================================
echo   Starting Customer Feedback Intelligence Dashboard
echo ========================================================
echo.

echo [1/3] Initializing database schema...
python backend\init_db.py
echo.

echo [2/3] Starting FastAPI Backend on port 8000...
start "FastAPI Backend (Port 8000)" cmd /k "python -m uvicorn app.main:app --port 8000 --app-dir backend"

timeout /t 2 /nobreak >nul

echo [3/3] Starting Streamlit Frontend on port 8501...
start "Streamlit Dashboard (Port 8501)" cmd /k "streamlit run frontend\streamlit_app.py"

echo.
echo ========================================================
echo   Application successfully started!
echo   Frontend: http://localhost:8501
echo   Backend:  http://localhost:8000/docs
echo ========================================================
echo.
pause
