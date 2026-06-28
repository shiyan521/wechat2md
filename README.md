# wechat2md

> 一键将微信 Mac 版收藏的文章批量导出为本地 Markdown 文件。

[![Python](https://img.shields.io/badge/Python-3.6%2B-blue)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-macOS%20%7C%20Linux%20%7C%20Windows-lightgrey)]()
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

## ✨ 特点

- **零依赖**：仅需系统自带 Python 3，不装任何第三方库
- **完全本地**：不经过任何第三方服务器，文章内容不过手
- **干净输出**：标题自动抓取，正文转标准 Markdown，图片链接保留
- **无风控风险**：只监听你主动复制的内容，不模拟点击、不绕登录

## 🚀 快速开始

```bash
git clone https://github.com/shiyan521/wechat2md.git
cd wechat2md
chmod +x export.sh
./export.sh
```

然后按终端提示操作：

1. **Phase 1 — 收集链接**：切换到微信 → 收藏 → 逐篇右键「复制链接」
2. 全部复制完，切回终端按 `Ctrl+C`
3. **Phase 2 — 下载 Markdown**：脚本自动逐篇下载转换

Markdown 文件保存在桌面 `wechat_md/` 目录。

## 📁 文件说明

| 文件 | 用途 |
|------|------|
| `export.sh` | 一键启动（收集 → 下载） |
| `clipboard_monitor.py` | 剪贴板监听，自动收集链接 |
| `download_markdown.py` | 访问文章页面，HTML → Markdown 转换 |

## 🛠 分步使用（高级）

如果不想一键跑，也可以分步执行：

```bash
# 第一步：只收集链接（微信里逐一右键 → 复制链接，完成后 Ctrl+C）
python3 clipboard_monitor.py

# 第二步：批量下载为 Markdown
python3 download_markdown.py ~/Desktop/wechat_urls.txt ~/Desktop/wechat_md
```

## ❓ 常见问题

**Q：为什么不能全自动导出？**
微信 Mac 版是 Electron 应用，收藏列表不暴露给 macOS 辅助功能 API，无法通过脚本自动逐篇点击。本方案采用剪贴板监听，你手动点、脚本自动收，是目前最可靠的半自动方案。

**Q：会触发微信风控吗？**
不会。你做的只是「右键复制链接」——微信眼中的正常用户操作。脚本不模拟点击、不走非正常接口。

**Q：有些文章下载失败？**
微信部分文章需要登录才能看全文，脚本只能抓取公开内容。失败的链接终端会提示，可以手动打开补充。

**Q：图片显示不正常？**
脚本保留的是微信图片 CDN 链接，需要联网查看。如需离线图片，可配合图片批量下载工具使用。

## ⚠️ 免责声明

本工具仅供个人对已收藏文章的合理备份使用。请勿用于：
- 批量爬取他人公众号内容
- 未经授权转载或商用
- 任何违反微信公众平台服务协议的行为

使用者需自行承担合规责任。

## 📄 License

MIT License — 详见 [LICENSE](LICENSE) 文件。
