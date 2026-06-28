#!/bin/bash
# ============================================================
#  微信收藏文章 → Markdown 批量导出（Mac / Linux）
# ============================================================
#  用法:
#    chmod +x export.sh
#    ./export.sh
# ============================================================

set -e
DIR="$(cd "$(dirname "$0")" && pwd)"
URLS_FILE="$HOME/Desktop/wechat_urls.txt"
OUT_DIR="$HOME/Desktop/wechat_md"

echo "============================================"
echo "  微信收藏 → Markdown 批量导出"
echo "============================================"
echo ""
echo "Phase 1: 收集链接"
echo "----------------------------------------"
echo ""
echo "接下来请操作微信："
echo "  收藏 → 右键文章 → 复制链接（逐一操作）"
echo "  全部完成后切回这里按 Ctrl+C"
echo ""
python3 "$DIR/clipboard_monitor.py"

echo ""
echo "Phase 2: 下载 Markdown"
echo "----------------------------------------"
python3 "$DIR/download_markdown.py" "$URLS_FILE" "$OUT_DIR"

echo ""
echo "============================================"
echo "  完成！"
echo "  文件位置: $OUT_DIR"
echo "  终端打开: open '$OUT_DIR'"
echo "============================================"
