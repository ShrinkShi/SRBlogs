@echo off
chcp 65001 >nul
title Kill Local Port 8000

echo.
echo ========================================
echo   正在查找占用本机 8000 端口的进程...
echo ========================================
echo.

for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000" ^| findstr "LISTENING"') do (
    echo 发现监听 8000 的 PID: %%a
    echo 正在结束 PID %%a 及其子进程...
    taskkill /PID %%a /F /T
)

echo.
echo ========================================
echo   当前 8000 端口占用情况：
echo ========================================
netstat -ano | findstr ":8000"

echo.
echo 如果上面没有输出 LISTENING，说明 8000 端口已经释放。
echo 如果仍然有 LISTENING，说明有启动脚本或 IDE 正在自动重启后端。
echo.
pause