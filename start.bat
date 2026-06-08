@echo off
title RAG Website Chatbot
color 0A

echo.
echo  ================================
echo   RAG Website Chatbot
echo  ================================
echo.

set "BACKEND_DIR=%~dp0backend"
set "FRONTEND_DIR=%~dp0frontend"

:: Check if venv exists, if not create it
if not exist "%BACKEND_DIR%\venv\Scripts\activate.bat" (
    echo [SETUP] Virtual environment not found. Creating...
    cd /d "%BACKEND_DIR%"
    python -m venv venv
    echo [SETUP] Installing backend dependencies...
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
    echo [SETUP] Backend setup complete!
)

:: Check if node_modules exists, if not install
if not exist "%FRONTEND_DIR%\node_modules" (
    echo [SETUP] Frontend dependencies not found. Installing...
    cd /d "%FRONTEND_DIR%"
    call npm install
    echo [SETUP] Frontend setup complete!
)

:: Check if .env exists
if not exist "%BACKEND_DIR%\.env" (
    echo.
    echo  [ERROR] backend\.env file not found!
    echo  Please copy backend\.env.example to backend\.env
    echo  and add your GROQ_API_KEY
    echo.
    pause
    exit /b 1
)

:: Kill anything on port 8000 and 3000
echo Clearing ports...
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8000" ^| find "LISTENING"') do taskkill /f /pid %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| find ":3000" ^| find "LISTENING"') do taskkill /f /pid %%a >nul 2>&1

timeout /t 2 /nobreak >nul

echo [1/2] Starting Backend on http://127.0.0.1:8000 ...
start "RAG Backend" cmd /k "cd /d "%BACKEND_DIR%" && venv\Scripts\activate && uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"

echo Waiting for backend to load...
timeout /t 15 /nobreak >nul

echo [2/2] Starting Frontend on http://localhost:3000 ...
start "RAG Frontend" cmd /k "cd /d "%FRONTEND_DIR%" && npm start"

echo.
echo  Backend  -> http://127.0.0.1:8000
echo  API Docs -> http://127.0.0.1:8000/docs
echo  Frontend -> http://localhost:3000
echo.
echo  Browser will open automatically...
echo  Keep this window open while using the app.
pause