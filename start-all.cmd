@echo off
chcp 65001 >nul
setlocal

set "ROOT=%~dp0"

echo [SRBlogs] Starting backend, frontend and admin in separate windows...
start "SRBlogs Backend" cmd /k call "%ROOT%start-backend.cmd"
timeout /t 2 /nobreak >nul
start "SRBlogs Frontend" cmd /k call "%ROOT%start-frontend.cmd"
timeout /t 2 /nobreak >nul
start "SRBlogs Admin" cmd /k call "%ROOT%start-admin.cmd"

echo.
echo Backend docs: http://127.0.0.1:8000/docs
echo Frontend:     http://127.0.0.1:5173
echo Admin:        http://127.0.0.1:5174/admin/
echo Admin login:  admin / change-me
