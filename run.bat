@echo off
title MarketAI - Autonomous AI Marketing Campaign Platform
echo ================================================================
echo          MarketAI - Autonomous Multi-Agent Marketing OS
echo            B.Tech Major Project - Production Launcher
echo ================================================================
echo.

cd /d "%~dp0"

echo [1/3] Building latest Frontend Production Assets...
cd frontend
call npm run build
if %errorlevel% neq 0 (
    echo [ERROR] Frontend build failed.
    pause
    exit /b %errorlevel%
)
cd ..

echo.
echo [2/3] Initializing Backend Server...
cd backend
if not exist "venv\Scripts\python.exe" (
    echo [ERROR] Python virtual environment not found in backend\venv.
    pause
    exit /b 1
)

echo.
echo [3/3] Starting Full-Stack Server on http://127.0.0.1:5000 ...
echo Press Ctrl+C to stop the server.
echo.
start http://127.0.0.1:5000
.\venv\Scripts\python.exe app.py
pause
