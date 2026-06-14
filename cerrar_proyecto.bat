@echo off
setlocal

set "ROOT=%~dp0"
set "FRONTEND=%ROOT%frontend"

echo Cerrando Prototipo Denuncia Virtual PNP...

taskkill /FI "WINDOWTITLE eq Backend FastAPI - Denuncia PNP*" /T /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq Frontend React - Denuncia PNP*" /T /F >nul 2>&1

for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000" ^| findstr "LISTENING"') do (
  echo Cerrando proceso backend PID %%a
  taskkill /PID %%a /F >nul 2>&1
)

for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8010" ^| findstr "LISTENING"') do (
  echo Cerrando proceso backend PID %%a
  taskkill /PID %%a /F >nul 2>&1
)

for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5173" ^| findstr "LISTENING"') do (
  echo Cerrando proceso frontend PID %%a
  taskkill /PID %%a /F >nul 2>&1
)

echo.
echo Proyecto cerrado. Si quedo alguna ventana abierta, puedes cerrarla manualmente.
echo.
pause
