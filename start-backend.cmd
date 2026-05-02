@echo off
chcp 65001 >nul
setlocal

set "ROOT=%~dp0"
set "BACKEND=%ROOT%backend"
set "PORT=8000"

echo [SRBlogs] Backend startup
echo Root: %ROOT%

for /f "tokens=5" %%p in ('netstat -ano ^| findstr /R /C:":%PORT% .*LISTENING"') do (
  echo [ERROR] Port %PORT% is already in use by PID %%p.
  echo Stop it with: taskkill /PID %%p /F
  exit /b 1
)

cd /d "%BACKEND%"
if not exist ".env" if exist ".env.example" copy /Y ".env.example" ".env" >nul
if not exist ".venv\Scripts\python.exe" (
  echo [SETUP] Creating Python virtual environment...
  py -3.10 -m venv .venv
  if errorlevel 1 python -m venv .venv
  echo [SETUP] Installing backend dependencies...
  ".venv\Scripts\python.exe" -m pip install -U pip
  ".venv\Scripts\python.exe" -m pip install -r requirements.txt
)

echo [START] http://127.0.0.1:%PORT%/docs
".venv\Scripts\python.exe" -m uvicorn app.main:app --reload --host 127.0.0.1 --port %PORT%
