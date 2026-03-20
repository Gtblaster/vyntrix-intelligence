@echo off
echo Starting Vyntrix Intelligence Application...

REM Start Backend
echo Starting FastAPI Backend on port 8000...
cd backend
start "Vyntrix Backend" cmd /k ".\venv\Scripts\uvicorn.exe main:app --reload --port 8000"
cd ..

REM Start Frontend
echo Starting Frontend development server on port 3000...
start "Vyntrix Frontend" cmd /k "python -m http.server 3000"

echo Application started in separate windows!
echo Backend API available at: http://localhost:8000
echo Frontend accessible at: http://localhost:3000
pause
