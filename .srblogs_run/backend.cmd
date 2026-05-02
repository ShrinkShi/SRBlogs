@echo off
chcp 65001 >nul
title SRBlogs Backend - FastAPI
cd /d "C:\Users\ASUS\Desktop\SRBlogs\backend"
echo.
echo ========================================
echo   SRBlogs Backend - FastAPI
echo ========================================
echo 当前目录: %cd%
echo.
if not exist ".env" if exist ".env.example" copy /Y ".env.example" ".env"
if not exist ".venv\Scripts\python.exe" (
    echo [初始化] 创建 Python 虚拟环境...
    py -3.10 -m venv .venv
    if errorlevel 1 python -m venv .venv
    echo [初始化] 安装后端依赖...
    ".venv\Scripts\python.exe" -m pip install -U pip
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt
)
echo [启动] FastAPI: http://127.0.0.1:8000/docs
".venv\Scripts\python.exe" -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
echo.
echo [后端已退出]
pause
