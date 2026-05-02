@echo off
chcp 65001 >nul
title SRBlogs Admin - Vue
cd /d "C:\Users\ASUS\Desktop\SRBlogs\admin"
echo.
echo ========================================
echo   SRBlogs Admin - Vue
echo ========================================
echo 当前目录: %cd%
echo.
if not exist ".env.development" if exist ".env.development.example" copy /Y ".env.development.example" ".env.development"
if not exist "node_modules" (
    echo [初始化] 安装后台依赖...
    call npm install
)
echo [启动] Admin: http://127.0.0.1:5174/admin/
call npm run dev -- --host 127.0.0.1 --port 5174
echo.
echo [后台已退出]
pause
