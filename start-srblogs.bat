@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

title SRBlogs 一键启动器

set "ROOT=%~dp0"
set "BACKEND=%ROOT%backend"
set "FRONTEND=%ROOT%frontend"
set "ADMIN=%ROOT%admin"
set "RUN_DIR=%ROOT%.srblogs_run"

echo.
echo ========================================
echo   SRBlogs 一键启动器
echo ========================================
echo 项目目录: %ROOT%
echo.

if not exist "%BACKEND%\app\main.py" (
    echo [错误] 未找到后端入口: %BACKEND%\app\main.py
    pause
    exit /b 1
)

if not exist "%FRONTEND%\package.json" (
    echo [错误] 未找到前端 package.json: %FRONTEND%\package.json
    pause
    exit /b 1
)

if not exist "%ADMIN%\package.json" (
    echo [错误] 未找到后台 package.json: %ADMIN%\package.json
    pause
    exit /b 1
)

if not exist "%RUN_DIR%" mkdir "%RUN_DIR%"

echo [1/4] 生成后端启动脚本...

> "%RUN_DIR%\backend.cmd" (
    echo @echo off
    echo chcp 65001 ^>nul
    echo title SRBlogs Backend - FastAPI
    echo cd /d "%BACKEND%"
    echo echo.
    echo echo ========================================
    echo echo   SRBlogs Backend - FastAPI
    echo echo ========================================
    echo echo 当前目录: %%cd%%
    echo echo.
    echo if not exist ".env" if exist ".env.example" copy /Y ".env.example" ".env"
    echo if not exist ".venv\Scripts\python.exe" ^(
    echo     echo [初始化] 创建 Python 虚拟环境...
    echo     py -3.10 -m venv .venv
    echo     if errorlevel 1 python -m venv .venv
    echo     echo [初始化] 安装后端依赖...
    echo     ".venv\Scripts\python.exe" -m pip install -U pip
    echo     ".venv\Scripts\python.exe" -m pip install -r requirements.txt
    echo ^)
    echo echo [启动] FastAPI: http://127.0.0.1:8000/docs
    echo ".venv\Scripts\python.exe" -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
    echo echo.
    echo echo [后端已退出]
    echo pause
)

echo [2/4] 生成前端启动脚本...

> "%RUN_DIR%\frontend.cmd" (
    echo @echo off
    echo chcp 65001 ^>nul
    echo title SRBlogs Frontend - Vue
    echo cd /d "%FRONTEND%"
    echo echo.
    echo echo ========================================
    echo echo   SRBlogs Frontend - Vue
    echo echo ========================================
    echo echo 当前目录: %%cd%%
    echo echo.
    echo if not exist ".env.development" if exist ".env.development.example" copy /Y ".env.development.example" ".env.development"
    echo if not exist "node_modules" ^(
    echo     echo [初始化] 安装前端依赖...
    echo     call npm install
    echo ^)
    echo echo [启动] Frontend: http://127.0.0.1:5173
    echo call npm run dev -- --host 127.0.0.1 --port 5173
    echo echo.
    echo echo [前端已退出]
    echo pause
)

echo [3/4] 生成后台启动脚本...

> "%RUN_DIR%\admin.cmd" (
    echo @echo off
    echo chcp 65001 ^>nul
    echo title SRBlogs Admin - Vue
    echo cd /d "%ADMIN%"
    echo echo.
    echo echo ========================================
    echo echo   SRBlogs Admin - Vue
    echo echo ========================================
    echo echo 当前目录: %%cd%%
    echo echo.
    echo if not exist ".env.development" if exist ".env.development.example" copy /Y ".env.development.example" ".env.development"
    echo if not exist "node_modules" ^(
    echo     echo [初始化] 安装后台依赖...
    echo     call npm install
    echo ^)
    echo echo [启动] Admin: http://127.0.0.1:5174/admin/
    echo call npm run dev -- --host 127.0.0.1 --port 5174
    echo echo.
    echo echo [后台已退出]
    echo pause
)

echo [4/4] 启动三个服务窗口...

start "SRBlogs Backend - FastAPI" cmd /k call "%RUN_DIR%\backend.cmd"
timeout /t 2 /nobreak >nul

start "SRBlogs Frontend - Vue" cmd /k call "%RUN_DIR%\frontend.cmd"
timeout /t 2 /nobreak >nul

start "SRBlogs Admin - Vue" cmd /k call "%RUN_DIR%\admin.cmd"

echo.
echo.
echo 默认后台账号:
echo admin / change-me
echo.
echo 如果浏览器页面刚打开时报错，等终端编译完成后刷新。
echo ========================================
echo.
pause