@echo off
chcp 65001 >nul
echo ===========================================
echo   微信收藏链接收集器（Windows 版）
echo ===========================================
echo.
echo   操作：微信收藏 → 右键文章 → 复制链接
echo   效果：每篇自动显示标题 + 链接
echo   结束：全部完成后按 Ctrl+C
echo.
python clipboard_monitor.py
pause
