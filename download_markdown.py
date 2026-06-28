#!/usr/bin/env python3
"""
微信文章批量下载为 Markdown
用法: python3 download_markdown.py <urls文件> <输出目录>

支持的输入格式：
  - 纯链接（一行一个）
  - 标题+链接（### 标题\n链接）
"""

import sys, os, re, ssl, time
import urllib.request
import urllib.error
import html as html_mod

def fetch_page(url, timeout=15):
    """抓取微信文章页面 HTML"""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    }
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
        return resp.read().decode('utf-8', errors='replace')

def extract_title(html_text):
    """多策略提取文章标题（与 clipboard_monitor 对齐）"""
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
        m = re.search(pat, html_text, flags)
        if m:
            title = html_mod.unescape(m.group(1).strip())
            title = re.sub(r'<[^>]+>', '', title).strip()
            title = re.sub(r'\s+', ' ', title)
            if len(title) > 2 and title != '微信公众平台':
                return title

    return None

def extract_author(html_text):
    """提取公众号名称"""
    patterns = [
        r'<meta[^>]*property="og:article:author"[^>]*content="([^"]+)"',
        r'var\s+nickname\s*=\s*[\'"]([^\'"]+)[\'"]',
        r'id="js_name"[^>]*>(.*?)<',
        r'class="rich_media_meta_nickname"[^>]*>(.*?)<',
    ]
    for pat in patterns:
        m = re.search(pat, html_text, re.DOTALL)
        if m:
            author = html_mod.unescape(m.group(1).strip())
            author = re.sub(r'<[^>]+>', '', author)
            if author:
                return author
    return None

def extract_body(html_text):
    """提取正文并转为 Markdown"""
    # 先试 js_content
    m = re.search(r'<div[^>]+id="js_content"[^>]*>(.*?)</div>\s*(?:<script|<div\s+id="js_pc_qr_code")', html_text, re.DOTALL)
    if not m:
        # 再试 rich_media_content
        m = re.search(r'<div[^>]+class="rich_media_content[^"]*"[^>]*>(.*?)</div>', html_text, re.DOTALL)
    if not m:
        return None

    body = m.group(1)
    return html_to_markdown(body)

def html_to_markdown(text):
    """HTML → Markdown"""
    # 去 script/style
    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)

    # 段落
    text = re.sub(r'<p[^>]*>', '\n\n', text)
    text = re.sub(r'</p>', '', text)
    text = re.sub(r'<br\s*/?>', '\n', text)

    # 图片
    text = re.sub(r'<img[^>]+data-src="([^"]+)"[^>]*>', r'\n\n![](\1)\n\n', text)
    text = re.sub(r'<img[^>]+src="([^"]+)"[^>]*>', r'\n\n![](\1)\n\n', text)
    text = re.sub(r'<img[^>]+>', '', text)

    # 加粗
    text = re.sub(r'<(?:strong|b)[^>]*>(.*?)</(?:strong|b)>', r'**\1**', text, flags=re.DOTALL)

    # 斜体
    text = re.sub(r'<(?:em|i)[^>]*>(.*?)</(?:em|i)>', r'*\1*', text, flags=re.DOTALL)

    # 标题
    text = re.sub(r'<h1[^>]*>(.*?)</h1>', r'\n# \1\n', text, flags=re.DOTALL)
    text = re.sub(r'<h2[^>]*>(.*?)</h2>', r'\n## \1\n', text, flags=re.DOTALL)
    text = re.sub(r'<h3[^>]*>(.*?)</h3>', r'\n### \1\n', text, flags=re.DOTALL)

    # 链接
    text = re.sub(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', r'[\2](\1)', text, flags=re.DOTALL)

    # 列表
    text = re.sub(r'<li[^>]*>', '\n- ', text)
    text = re.sub(r'</li>', '', text)

    # 引用
    text = re.sub(r'<blockquote[^>]*>', '\n> ', text)
    text = re.sub(r'</blockquote>', '\n', text)

    # 代码
    text = re.sub(r'<code[^>]*>(.*?)</code>', r'`\1`', text, flags=re.DOTALL)
    text = re.sub(r'<pre[^>]*>(.*?)</pre>', r'\n```\n\1\n```\n', text, flags=re.DOTALL)

    # 去掉 span/div 保留内容
    text = re.sub(r'<(?:span|div|section|header|footer|nav)[^>]*>', '', text)
    text = re.sub(r'</(?:span|div|section|header|footer|nav)>', '', text)

    # 去掉剩余标签
    text = re.sub(r'<[^>]+>', '', text)

    # HTML 实体
    text = html_mod.unescape(text)

    # 清理空行和空白
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'^[ \t]+', '', text, flags=re.MULTILINE)
    text = text.strip()

    return text

def sanitize_filename(name):
    """清理文件名"""
    name = re.sub(r'[\\/:*?"<>|]', '_', name)
    return name[:100].strip()

def read_urls(filepath):
    """
    读取 URL 列表，支持两种格式：
    1. ### 标题\n链接  (clipboard_monitor 输出格式)
    2. 纯链接（一行一个）
    返回 [(title_or_None, url), ...]
    """
    entries = []
    with open(filepath) as f:
        content = f.read()

    # 尝试解析标题+链接格式
    title_url = re.findall(r'###\s*(.+?)\n\s*(https?://[^\s]+)', content)
    if title_url:
        for t, u in title_url:
            entries.append((t.strip(), u.strip()))
        return entries

    # 纯链接格式
    for line in content.split('\n'):
        line = line.strip()
        if line and line.startswith('http'):
            entries.append((None, line))

    return entries

def main():
    if len(sys.argv) < 2:
        print("用法: python3 download_markdown.py <urls文件> [输出目录]")
        print("示例: python3 download_markdown.py ~/Desktop/wechat_urls.txt ./wechat_md")
        sys.exit(1)

    urls_file = sys.argv[1]
    out_dir = sys.argv[2] if len(sys.argv) > 2 else os.path.expanduser("~/Desktop/wechat_md")

    if not os.path.exists(urls_file):
        print(f"❌ 文件不存在: {urls_file}")
        sys.exit(1)

    os.makedirs(out_dir, exist_ok=True)

    entries = read_urls(urls_file)
    total = len(entries)

    print(f"共 {total} 篇文章，开始下载...")
    print()

    success = 0
    for i, (known_title, url) in enumerate(entries, 1):
        short_url = url[:70]
        print(f"[{i}/{total}] {short_url}...")

        try:
            raw = fetch_page(url)

            # 从网页 HTML 提取标题
            page_title = extract_title(raw)
            author = extract_author(raw)

            # 标题优先级：已知标题 > 网页标题 > URL 做标识
            if known_title and len(known_title) > 2:
                title = known_title
            elif page_title:
                title = page_title
            else:
                # 用 URL 路径做标题
                title = url.split('/')[-1][:50] or url.split('/')[-2]

            # 提取正文
            body = extract_body(raw)
            if body is None:
                # 正文提取失败，可能被隐藏了
                print(f"  ⚠️  正文提取失败，保存链接信息")
                body = f"（正文提取失败，请手动访问原文）\n\n原文链接：{url}"

            # 生成文件名和路径
            fname = sanitize_filename(title) + '.md'
            fpath = os.path.join(out_dir, fname)

            # 处理重名
            counter = 1
            while os.path.exists(fpath):
                fname = sanitize_filename(title) + f'_{counter}.md'
                fpath = os.path.join(out_dir, fname)
                counter += 1

            # 写入 Markdown
            author_line = f"\n> 来源：{author}\n" if author else ""
            with open(fpath, 'w', encoding='utf-8') as f:
                f.write(f"# {title}\n")
                if author_line:
                    f.write(author_line)
                f.write(f"\n> 原文链接：{url}\n")
                f.write(f"> 下载时间：{time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write(body)

            print(f"  ✅ {title[:60]}")
            success += 1
            time.sleep(0.5)

        except urllib.error.HTTPError as e:
            print(f"  ❌ HTTP {e.code}")
        except urllib.error.URLError as e:
            print(f"  ❌ 网络错误: {e.reason}")
        except Exception as e:
            print(f"  ❌ {e}")

    print()
    print(f"✅ 完成！成功 {success}/{total} 篇")
    print(f"📂 保存至: {out_dir}")

if __name__ == '__main__':
    main()
