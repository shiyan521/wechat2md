#!/usr/bin/env python3
"""微信收藏链接收集 — 纯链接版。Ctrl+C 停止。"""

import subprocess, time, re, os

OUTPUT = os.path.expanduser("~/Desktop/wechat_urls.txt")
URL_RE = re.compile(r'https?://[^\s"\u4e00-\u9fff\uff00-\uffef]+')

def cb():
    try:
        r = subprocess.run(['pbpaste'], capture_output=True, text=True, timeout=2)
        return r.stdout.strip()
    except:
        return ""

last = cb()
seen = set()

print("运行中… 微信收藏里 右键→复制链接。完成后切回这里按 Ctrl+C\n")

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
            if url not in seen:
                seen.add(url)
                with open(OUTPUT, 'a') as f:
                    f.write(url + '\n')
                print(f"[{len(seen)}] {url}")
        else:
            print(f"⚠️  未识别: {cur[:80].replace(chr(10),' ')}")
except KeyboardInterrupt:
    print(f"\n✅ {len(seen)} 篇，保存至 {OUTPUT}")
