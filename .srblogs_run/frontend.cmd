@echo off
chcp 65001 >nul
title SRBlogs Frontend - Vue
cd /d "C:\Users\ASUS\Desktop\SRBlogs\frontend"
echo.
echo ========================================
echo   SRBlogs Frontend - Vue
echo ========================================
echo 当前目录: %cd%
echo.
if not exist ".env.development" if exist ".env.development.example" copy /Y ".env.development.example" ".env.development"
if not exist "node_modules" (
    echo [初始化] 安装前端依赖...
    call npm install
)
echo [启动] Frontend: http://127.0.0.1:5173
call npm run dev -- --host 127.0.0.1 --port 5173
echo.
echo [前端已退出]
pause
