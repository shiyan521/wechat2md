# wechat2md

> 将微信收藏的文章批量导出为本地 Markdown 文件（Mac / Windows / Linux 通用）

[![Python](https://img.shields.io/badge/Python-3.6%2B-blue)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-macOS%20%7C%20Windows%20%7C%20Linux-lightgrey)]()
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

## ✨ 特点

- **零依赖**：仅需系统自带 Python 3，不装任何第三方库
- **跨平台**：Mac / Windows / Linux 全部支持
- **完全本地**：不经过任何第三方服务器
- **实时标题**：每复制一篇链接立刻从网页抓取标题
- **干净输出**：正文转标准 Markdown，图片链接保留

---

## 🚀 快速开始

### Mac / Linux

```bash
git clone https://github.com/shiyan521/wechat2md.git
cd wechat2md
chmod +x export.sh
./export.sh
```

### Windows

双击 `step1_collect.bat` 收集链接，再双击 `step2_download.bat` 下载 Markdown。

或者用命令行：

```cmd
python clipboard_monitor.py
python download_markdown.py %USERPROFILE%\Desktop\wechat_urls.txt %USERPROFILE%\Desktop\wechat_md
```

---

## 📖 操作步骤

1. 运行脚本 → 终端显示「等待复制链接…」
2. 微信 → 收藏 → **右键**文章 → **复制链接**（逐篇操作）
3. 每篇自动显示标题 ✅ 全部完成后按 `Ctrl+C`
4. 脚本自动批量下载为 Markdown

完成后打开文件夹：

| 系统 | 命令 |
|------|------|
| Mac | `open ~/Desktop/wechat_md` |
| Windows | `start "" "%USERPROFILE%\Desktop\wechat_md"` |
| Linux | `xdg-open ~/Desktop/wechat_md` |

> 📖 详细图文指南见 [操作指南.md](操作指南.md)

---

## 📁 文件说明

| 文件 | 用途 |
|------|------|
| `export.sh` | Mac / Linux 一键脚本 |
| `step1_collect.bat` | Windows 收集链接 |
| `step2_download.bat` | Windows 下载 Markdown |
| `clipboard_monitor.py` | 剪贴板监听，实时抓取标题 |
| `download_markdown.py` | 文章下载，HTML → MD 转换 |
| `操作指南.md` | 完整操作手册 |

---

## ❓ 常见问题

| 问题 | 解决 |
|------|------|
| 标题显示「未能获取」 | 网络超时，Ctrl+C 后自动重试 |
| 下载的 MD 没有图片 | 已保留为远程链接，需联网查看 |
| Windows 报 `python` 不是命令 | 安装 Python 3 并勾选「Add to PATH」 |
| 会触发微信风控吗？ | 不会，只是监听右键复制链接 |

---

## ⚠️ 免责声明

本工具仅供个人对已收藏文章的合理备份使用。请勿用于批量爬取他人公众号内容、未经授权转载或商用。

## 📄 License

MIT License — 详见 [LICENSE](LICENSE)
