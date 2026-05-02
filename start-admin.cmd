@echo off
chcp 65001 >nul
setlocal

set "ROOT=%~dp0"
set "ADMIN=%ROOT%admin"
set "PORT=5174"

echo [SRBlogs] Admin startup
echo Root: %ROOT%

for /f "tokens=5" %%p in ('netstat -ano ^| findstr /R /C:":%PORT% .*LISTENING"') do (
  echo [ERROR] Port %PORT% is already in use by PID %%p.
  echo Stop it with: taskkill /PID %%p /F
  exit /b 1
)

cd /d "%ADMIN%"
if not exist ".env.development" if exist ".env.development.example" copy /Y ".env.development.example" ".env.development" >nul
if not exist "node_modules" (
  echo [SETUP] Installing admin dependencies...
  call npm.cmd install
)

echo [START] http://127.0.0.1:%PORT%/admin/
call npm.cmd run dev -- --host 127.0.0.1 --port %PORT% --strictPort
