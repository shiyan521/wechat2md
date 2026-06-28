#!/bin/bash
# ============================================================
#  微信收藏文章 → Markdown 批量导出（Mac / Linux）
# ============================================================
#  用法:
#    chmod +x export.sh
#    ./export.sh
# ============================================================

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

# 自动检测 Python 3
PYTHON=""
for cmd in python3 python; do
    if command -v "$cmd" &>/dev/null; then
        ver=$("$cmd" --version 2>&1)
        if [[ "$ver" == *"Python 3"* ]]; then
            PYTHON="$cmd"
            break
        fi
    fi
done

if [ -z "$PYTHON" ]; then
    echo "❌ 未找到 Python 3！请先安装 Python 3"
    echo "   macOS: brew install python3"
    exit 1
fi

echo "[检测到: $PYTHON]"
echo ""

# Ctrl+C 退出码 130，其他错误退出码非零
$PYTHON "$DIR/clipboard_monitor.py"
PHASE1_EXIT=$?

if [ $PHASE1_EXIT -ne 0 ] && [ $PHASE1_EXIT -ne 130 ]; then
    echo ""
    echo "❌ Phase 1 异常退出（错误码: $PHASE1_EXIT）"
    exit $PHASE1_EXIT
fi

echo ""
echo "Phase 2: 下载 Markdown"
echo "----------------------------------------"
$PYTHON "$DIR/download_markdown.py" "$URLS_FILE" "$OUT_DIR"

echo ""
echo "============================================"
echo "  完成！"
echo "  文件位置: $OUT_DIR"
echo "============================================"

# 自动打开文件夹
open "$OUT_DIR" 2>/dev/null || echo "  终端打开: open '$OUT_DIR'"
