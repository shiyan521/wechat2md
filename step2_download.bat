@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ===========================================
echo   微信文章 Markdown 下载器（Windows 版）
echo ===========================================
echo.

:: 检查 URLs 文件是否存在
set URLS_FILE=%USERPROFILE%\Desktop\wechat_urls.txt
if not exist "%URLS_FILE%" (
    echo ❌ 未找到 %URLS_FILE%
    echo    请先运行 step1_collect.bat 收集链接！
    pause
    exit /b 1
)

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
echo [URLs 文件: %URLS_FILE%]
echo.

set OUT_DIR=%USERPROFILE%\Desktop\wechat_md
%PYTHON_CMD% download_markdown.py "%URLS_FILE%" "%OUT_DIR%"
echo.
echo 📂 文件已保存到桌面 wechat_md 文件夹
echo    打开文件夹命令: start "" "%OUT_DIR%"
echo.
start "" "%OUT_DIR%"
pause
