@echo off
chcp 65001 >nul
echo ===========================================
echo   微信文章 Markdown 下载器（Windows 版）
echo ===========================================
echo.
python download_markdown.py wechat_urls.txt wechat_md
echo.
echo 下载完成！文件在 wechat_md 文件夹里。
pause
