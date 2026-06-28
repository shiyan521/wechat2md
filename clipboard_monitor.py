#!/usr/bin/env python3
"""
微信收藏链接收集 — 自动抓取标题版
用法: python3 clipboard_monitor.py
- 监听剪贴板，自动收集微信文章链接
- Ctrl+C 后自动从网页抓取每篇文章标题
- 结果保存为「标题 ||| 链接」格式
"""

import subprocess, time, re, os, sys, ssl
import urllib.request, urllib.error
import html as html_mod

OUTPUT = os.path.expanduser("~/Desktop/wechat_urls.txt")
URL_RE = re.compile(r'https?://[^\s"\u4e00-\u9fff\uff00-\uffef]+')

def cb():
    try:
        r = subprocess.run(['pbpaste'], capture_output=True, text=True, timeout=2)
        return r.stdout.strip()
    except:
        return ""

def fetch_title(url, timeout=10):
    """快速抓取文章标题，不下载全文"""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            raw = resp.read().decode('utf-8', errors='replace')
    except Exception:
        return ""

    # 多重策略提取标题
    patterns = [
        # 1. og:title meta (最常见)
        r'<meta[^>]*property="og:title"[^>]*content="([^"]+)"',
        r"<meta[^>]*property='og:title'[^>]*content='([^']+)'",
        # 2. twitter:title
        r'<meta[^>]*name="twitter:title"[^>]*content="([^"]+)"',
        # 3. 网页 <title>
        r'<title>([^<]+)</title>',
        # 4. JavaScript 变量 (微信旧版)
        r'var\s+msg_title\s*=\s*["\']([^"\']+)["\']',
        r'var\s+title\s*=\s*["\']([^"\']+)["\']',
        # 5. rich_media_title
        r'class="rich_media_title[^"]*"[^>]*>(.*?)<',
        r'id="activity-name"[^>]*>(.*?)<',
        # 6. JSON article data
        r'"title"\s*:\s*"([^"]+)"',
    ]

    for pat in patterns:
        m = re.search(pat, raw, re.DOTALL)
        if m:
            title = html_mod.unescape(m.group(1).strip())
            title = re.sub(r'<[^>]+>', '', title)  # 去残留标签
            if len(title) > 2:  # 太短的不算
                return title.strip()

    return ""


# ---- 主流程 ----
last = cb()
seen = set()
url_list = []  # 保持顺序

print("=" * 50)
print(" 微信收藏链接收集器")
print("=" * 50)
print()
print("请到微信收藏里 → 右键文章 → 复制链接")
print("每复制一篇这里会显示，全部完成后按 Ctrl+C")
print()

try:
    while True:
        time.sleep(0.5)
        cur = cb()
        if cur == last or not cur:
            continue
        last = cur

        m = URL_RE.search(cur)
        if m:
            url = m.group(0).rstrip('"\'.。，,;；')
            # 去重（复用分享参数算同一篇）
            clean_url = re.sub(r'[?&](mpshare|scene|srcid|sharer_shareinfo|sharer_shareinfo_first)=[^&#]+', '', url)
            # 提取文章 ID 用于去重
            article_id = re.search(r'/s/([A-Za-z0-9_-]+)', url)
            if article_id:
                url_key = article_id.group(1)
            else:
                url_key = clean_url

            if url_key not in seen:
                seen.add(url_key)
                url_list.append(url)
                with open(OUTPUT, 'a') as f:
                    f.write(url + '\n')
                print(f"[{len(url_list)}] ✅ {url}")
            else:
                print(f"    ⏭️ 已跳过（重复）")
        else:
            # 看看剪贴板里是什么
            preview = cur[:80].replace('\n', ' ')
            print(f"⚠️  非链接: {preview}")

except KeyboardInterrupt:
    print()
    print(f"\n📄 共收集 {len(url_list)} 条链接")
    print("🔍 正在抓取文章标题...")
    print()

    # Phase 2: 逐篇获取标题
    results = []
    for i, url in enumerate(url_list, 1):
        print(f"[{i}/{len(url_list)}] 获取标题...", end=' ', flush=True)
        title = fetch_title(url)
        if title:
            print(f"✅ {title}")
        else:
            print(f"⚠️ 未能获取标题")
        results.append((title if title else "", url))
        time.sleep(0.3)

    # 写入带标题的文件
    with open(OUTPUT, 'w') as f:
        for title, url in results:
            if title:
                f.write(f"### {title}\n{url}\n\n")
            else:
                f.write(f"{url}\n\n")

    print()
    print("=" * 50)
    print(f"✅ {len(results)} 篇文章，标题 + 链接已保存")
    print(f"📄 {OUTPUT}")
    print("=" * 50)
