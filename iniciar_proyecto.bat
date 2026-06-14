@echo off
setlocal

set "ROOT=%~dp0"
set "BACKEND=%ROOT%backend"
set "FRONTEND=%ROOT%frontend"

echo Iniciando Prototipo Denuncia Virtual PNP...

if not exist "%BACKEND%\.venv\Scripts\python.exe" (
  echo [ERROR] No se encontro el entorno virtual del backend.
  echo Ejecuta primero:
  echo   cd backend
  echo   python -m venv .venv
  echo   .venv\Scripts\pip install -r requirements.txt
  pause
  exit /b 1
)

if not exist "%FRONTEND%\node_modules" (
  echo [ERROR] No se encontro node_modules del frontend.
  echo Ejecuta primero:
  echo   cd frontend
  echo   npm install
  pause
  exit /b 1
)

start "Backend FastAPI - Denuncia PNP" cmd /k "cd /d ""%BACKEND%"" && .venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8010 --reload"
start "Frontend React - Denuncia PNP" cmd /k "cd /d ""%FRONTEND%"" && npm run dev -- --port 5173"

echo.
echo Proyecto iniciado.
echo Backend:  http://127.0.0.1:8010/docs
echo Frontend: http://127.0.0.1:5173
echo.
pause
