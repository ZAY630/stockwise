@echo off
title StockWise - AI Stock Investment Platform

echo ========================================
echo   StockWise - Starting Up...
echo ========================================
echo.

:: Find Python (check PATH first, then common install locations)
set PYTHON_EXE=
where python >nul 2>&1
if %ERRORLEVEL% equ 0 (
    set PYTHON_EXE=python
) else (
    :: Search common Python install locations
    for /d %%d in ("%LOCALAPPDATA%\Programs\Python\Python3*") do (
        if exist "%%d\python.exe" set PYTHON_EXE=%%d\python.exe
    )
    if not defined PYTHON_EXE (
        for /d %%d in ("C:\Program Files\Python3*") do (
            if exist "%%d\python.exe" set PYTHON_EXE=%%d\python.exe
        )
    )
    if not defined PYTHON_EXE (
        for /d %%d in ("C:\Python3*") do (
            if exist "%%d\python.exe" set PYTHON_EXE=%%d\python.exe
        )
    )
)

if not defined PYTHON_EXE (
    echo [ERROR] Python 3.12+ is not installed.
    echo Please install from https://python.org
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

echo [✓] Found Python: %PYTHON_EXE%

:: Check for Node.js
where node >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Node.js is not installed or not in PATH.
    echo Please install Node.js 20+ from https://nodejs.org
    pause
    exit /b 1
)

:: Check for .env file
if not exist ".env" (
    echo [WARNING] .env file not found! Creating from .env.example...
    copy .env.example .env >nul
    echo [ACTION] Please edit .env and add your ANTHROPIC_API_KEY, then restart.
    start notepad .env
    pause
    exit /b 1
)

:: Check API key
findstr /C:"ANTHROPIC_API_KEY=your-api-key-here" .env >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo [ERROR] ANTHROPIC_API_KEY is not set in .env!
    echo [ACTION] Edit .env and replace "your-api-key-here" with your real API key.
    start notepad .env
    pause
    exit /b 1
)

echo [✓] Prerequisites checked

:: Copy .env to backend directory (where config.py looks for it)
if not exist "apps\backend\.env" (
    echo [*] Copying .env to backend directory...
    copy .env apps\backend\.env >nul
    echo [✓] .env copied
)

:: Setup Backend
echo.
echo --- Setting up Backend ---
cd apps\backend

if not exist ".venv" (
    echo [*] Creating Python virtual environment...
    %PYTHON_EXE% -m venv .venv
    echo [✓] Virtual environment created
)

echo [*] Installing Python dependencies...
call .venv\Scripts\activate.bat
pip install -q -e ".[dev]"
echo [✓] Backend dependencies ready

:: Install frontend deps if needed
echo.
echo --- Setting up Frontend ---
cd ..\..\apps\frontend

where pnpm >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [*] Installing pnpm...
    npm install -g pnpm
)

if not exist "node_modules" (
    echo [*] Installing frontend dependencies (this may take a minute)...
    call pnpm install
    echo [✓] Frontend dependencies installed
)

:: Return to root and launch
cd ..\..

echo.
echo ========================================
echo   Starting StockWise...
echo ========================================
echo.
echo   Backend  → http://localhost:8000
echo   Frontend → http://localhost:3000
echo   API Docs → http://localhost:8000/docs
echo.
echo   Press Ctrl+C in each window to stop.
echo ========================================
echo.

:: Start backend in a new window (use venv python directly, no PATH needed)
start "StockWise Backend" cmd /c "cd apps\backend && .venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000"

:: Brief pause to let backend start
timeout /t 3 /nobreak >nul

:: Start frontend in a new window
start "StockWise Frontend" cmd /c "cd apps\frontend && pnpm dev"

echo [✓] StockWise is starting up! Opening browser...
timeout /t 5 /nobreak >nul
start http://localhost:3000

echo.
echo Both servers are running. Close their windows to stop.
pause
