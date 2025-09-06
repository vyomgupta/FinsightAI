@echo off
echo Starting FinSightAI Full Stack Application...
echo.

REM Load environment variables from .env file, ignoring comments
for /f "usebackq delims=" %%a in (`findstr /v "^#" .env`) do set "%%a"

REM Start the backend in a new window
echo Starting FastAPI Backend...
start "FinSightAI Backend" cmd /k "cd api && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"

REM Wait a moment for backend to start
timeout /t 3 /nobreak > nul

REM Start the frontend
echo Starting React Frontend...
cd web
start "FinSightAI Frontend" cmd /k "npm start"

echo.
echo FinSightAI is starting up...
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo.
echo Both services will open in separate command windows.
pause
