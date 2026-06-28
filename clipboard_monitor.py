#!/usr/bin/env python3
"""
微信收藏链接收集 — 实时抓取标题版
用法: python3 clipboard_monitor.py
- 监听剪贴板，每复制一篇链接立刻从网页抓取标题
- 去重逻辑：按文章 /s/ 后的 ID 去重
- 结果保存为「### 标题\n链接」格式
"""
import subprocess, time, re, os, ssl, sys
import urllib.request, urllib.error
import html as html_mod
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError

OUTPUT = os.path.expanduser("~/Desktop/wechat_urls.txt")
URL_RE = re.compile(r'https?://[^\s"\u4e00-\u9fff\uff00-\uffef]+')

# ========== 标题抓取 ==========

def fetch_title(url, timeout=8):
    """
    从微信文章页面抓取标题。
    多重策略：og:title → msg_title JS变量 → <title> → rich_media_title → JSON data
    """
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'),
            'Accept': 'text/html,application/xhtml+xml',
        })
        resp = urllib.request.urlopen(req, timeout=timeout, context=ctx)
        raw = resp.read().decode('utf-8', errors='replace')
    except Exception as e:
        return None

    # 多策略匹配（按可靠性排序）
    patterns = [
        # 1. og:title — 最可靠
        (r'<meta[^>]*property="og:title"[^>]*content="([^"]+)"', False),
        # 2. JS 变量 msg_title
        (r"var\s+msg_title\s*=\s*'([^']+)'", False),
        (r'var\s+msg_title\s*=\s*"([^"]+)"', False),
        # 3. 网页 <title>
        (r'<title>([^<]+)</title>', False),
        # 4. rich_media_title / activity-name
        (r'id="activity-name"[^>]*>\s*([^<]+)', True),
        (r'class="rich_media_title[^"]*"[^>]*>\s*([^<]+)', True),
        # 5. JSON 内嵌 data
        (r'"title"\s*:\s*"([^"]+)"', False),
    ]

    for pat, is_dotall in patterns:
        flags = re.DOTALL if is_dotall else 0
        m = re.search(pat, raw, flags)
        if m:
            title = html_mod.unescape(m.group(1).strip())
            title = re.sub(r'<[^>]+>', '', title).strip()  # 去残留 HTML
            title = re.sub(r'\s+', ' ', title)              # 合并空白
            if len(title) >= 2:
                return title

    return None


# ========== 去重 & URL 清洗 ==========

def url_key(url):
    """提取文章唯一 ID，用于去重"""
    # 优先 /s/XXXXX 格式
    m = re.search(r'/s/([A-Za-z0-9_-]+)', url)
    if m:
        return m.group(1)
    # 其次用 sn 参数
    m = re.search(r'[?&]sn=([A-Za-z0-9]+)', url)
    if m:
        return m.group(1)
    # 最后用完整 URL（去掉分享参数）
    clean = re.sub(r'[?&](mpshare|scene|srcid|sharer_shareinfo|sharer_shareinfo_first)=[^&#]+', '', url)
    return clean.rstrip('#rd')


# ========== 主流程 ==========

def main():
    # 清空输出文件
    with open(OUTPUT, 'w') as f:
        f.write('')

    last = cb()
    seen = set()
    entries = []  # [(title_or_None, url), ...]
    fetch_failures = 0

    print("=" * 55)
    print("  微信收藏链接收集器（实时标题版）")
    print("=" * 55)
    print()
    print("  操作：微信收藏 → 右键文章 → 复制链接")
    print("  效果：每篇自动显示标题 + 链接")
    print("  结束：全部完成后按 Ctrl+C")
    print()

    try:
        while True:
            time.sleep(0.5)
            cur = cb()
            if cur == last or not cur:
                continue
            last = cur

            m = URL_RE.search(cur)
            if not m:
                preview = cur[:80].replace('\n', ' ')
                print(f"  ⚠️  非链接: {preview}")
                continue

            url = m.group(0).rstrip('"\'.。，,;；')
            key = url_key(url)

            if key in seen:
                print(f"  ⏭️  已跳过（重复）")
                continue

            seen.add(key)
            idx = len(entries) + 1

            # 立刻抓标题
            print(f"  [{idx}] 获取标题...", end=' ', flush=True)
            title = None
            try:
                with ThreadPoolExecutor(max_workers=1) as ex:
                    future = ex.submit(fetch_title, url, 8)
                    title = future.result(timeout=10)
            except (FuturesTimeoutError, Exception):
                pass

            if title:
                print(f"✅ {title}")
            else:
                print(f"⚠️  未能获取标题（链接已保存，Ctrl+C 后重试）")
                fetch_failures += 1

            entries.append((title, url))

    except KeyboardInterrupt:
        print()
        print(f"  📄 共收集 {len(entries)} 篇文章")
        print()

        # 重试失败的标题
        retry_count = 0
        for i, (t, url) in enumerate(entries):
            if t is None:
                print(f"  [{i+1}] 重试获取标题...", end=' ', flush=True)
                try:
                    with ThreadPoolExecutor(max_workers=1) as ex:
                        future = ex.submit(fetch_title, url, 12)
                        t = future.result(timeout=15)
                except (FuturesTimeoutError, Exception):
                    pass
                if t:
                    entries[i] = (t, url)
                    print(f"✅ {t}")
                    retry_count += 1
                else:
                    print(f"❌ 仍然失败")
                time.sleep(0.3)

        if retry_count:
            print(f"  🔄 重试成功 {retry_count} 篇")
        print()

        # 写入文件
        missing = 0
        with open(OUTPUT, 'w') as f:
            for title, url in entries:
                if title:
                    f.write(f"### {title}\n{url}\n\n")
                else:
                    f.write(f"{url}\n\n")
                    missing += 1

        print("=" * 55)
        print(f"  ✅ {len(entries)} 篇文章已保存")
        if missing:
            print(f"  ⚠️  {missing} 篇未能获取标题（链接已保存）")
        print(f"  📄 {OUTPUT}")
        print("=" * 55)


def cb():
    try:
        r = subprocess.run(['pbpaste'], capture_output=True, text=True, timeout=2)
        return r.stdout.strip()
    except:
        return ""


if __name__ == '__main__':
    main()
