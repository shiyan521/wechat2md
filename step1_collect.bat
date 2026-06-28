@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ===========================================
echo   微信收藏链接收集器（Windows 版）
echo ===========================================
echo.
echo   操作：微信收藏 → 右键文章 → 复制链接
echo   效果：每篇自动显示标题 + 链接
echo   结束：全部完成后按 Ctrl+C
echo.

:: 自动检测 Python 命令
set PYTHON_CMD=
python3 --version >nul 2>&1 && set PYTHON_CMD=python3
if "%PYTHON_CMD%"=="" python --version >nul 2>&1 && set PYTHON_CMD=python
if "%PYTHON_CMD%"=="" py --version >nul 2>&1 && set PYTHON_CMD=py
if "%PYTHON_CMD%"=="" (
    echo ❌ 未找到 Python！请先安装 Python 3
    echo    下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [检测到 Python: %PYTHON_CMD%]
echo.
%PYTHON_CMD% clipboard_monitor.py
pause
