#!/usr/bin/env python3
"""
微信文章批量下载为 Markdown
用法: python3 wechat_to_md.py <urls文件> <输出目录>
"""

import sys, os, re, html, ssl, time
import urllib.request
import urllib.error

def fetch_page(url, timeout=15):
    """抓取微信文章页面 HTML"""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
        return resp.read().decode('utf-8', errors='replace')

def extract_article(html_text):
    """从 HTML 提取标题、作者、日期、正文"""
    data = {}

    # 标题: og:title > rich_media_title > <title>
    m = re.search(r'<meta[^>]+property="og:title"[^>]+content="([^"]+)"', html_text)
    if m:
        data['title'] = html.unescape(m.group(1).strip())
    else:
        m = re.search(r'<h1[^>]+class="rich_media_title[^"]*"[^>]*>(.*?)</h1>', html_text, re.DOTALL)
        if m:
            data['title'] = html.unescape(re.sub(r'<[^>]+>', '', m.group(1)).strip())
        else:
            m = re.search(r'<title>([^<]+)</title>', html_text)
            data['title'] = html.unescape(m.group(1).strip()) if m else "无标题"

    # 公众号名称
    m = re.search(r'<meta[^>]+property="og:article:author"[^>]+content="([^"]+)"', html_text)
    if m:
        data['author'] = html.unescape(m.group(1).strip())

    # 正文: js_content div
    m = re.search(r'<div[^>]+id="js_content"[^>]*>(.*?)</div>\s*<script', html_text, re.DOTALL)
    if not m:
        m = re.search(r'<div[^>]+class="rich_media_content[^"]*"[^>]*>(.*?)</div>', html_text, re.DOTALL)
    if not m:
        return data, "（正文提取失败）"

    body = m.group(1)
    body = html_to_markdown(body)
    return data, body

def html_to_markdown(text):
    """简单 HTML → Markdown 转换"""
    # 去掉 script/style
    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)

    # 段落
    text = re.sub(r'<p[^>]*>', '\n\n', text)
    text = re.sub(r'</p>', '', text)
    text = re.sub(r'<br\s*/?>', '\n', text)

    # 图片 → 保留链接
    text = re.sub(r'<img[^>]+data-src="([^"]+)"[^>]*>', r'\n\n![](\1)\n\n', text)
    text = re.sub(r'<img[^>]+src="([^"]+)"[^>]*>', r'\n\n![](\1)\n\n', text)
    text = re.sub(r'<img[^>]+>', '', text)

    # 加粗
    text = re.sub(r'<strong[^>]*>(.*?)</strong>', r'**\1**', text, flags=re.DOTALL)
    text = re.sub(r'<b>(.*?)</b>', r'**\1**', text, flags=re.DOTALL)

    # 标题
    text = re.sub(r'<h1[^>]*>(.*?)</h1>', r'\n# \1\n', text, flags=re.DOTALL)
    text = re.sub(r'<h2[^>]*>(.*?)</h2>', r'\n## \1\n', text, flags=re.DOTALL)
    text = re.sub(r'<h3[^>]*>(.*?)</h3>', r'\n### \1\n', text, flags=re.DOTALL)

    # 链接
    text = re.sub(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', r'[\2](\1)', text, flags=re.DOTALL)

    # 列表
    text = re.sub(r'<li[^>]*>', '\n- ', text)
    text = re.sub(r'</li>', '', text)

    # 区块引用
    text = re.sub(r'<blockquote[^>]*>', '\n> ', text)
    text = re.sub(r'</blockquote>', '\n', text)

    # 代码
    text = re.sub(r'<code[^>]*>(.*?)</code>', r'`\1`', text, flags=re.DOTALL)
    text = re.sub(r'<pre[^>]*>(.*?)</pre>', r'\n```\n\1\n```\n', text, flags=re.DOTALL)

    # 去掉 span 保留内容
    text = re.sub(r'<span[^>]*>', '', text)
    text = re.sub(r'</span>', '', text)

    # 去掉剩余标签
    text = re.sub(r'<[^>]+>', '', text)

    # 解析 HTML 实体
    text = html.unescape(text)

    # 清理多余空行
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'^\s+', '', text)

    return text.strip()

def sanitize_filename(name):
    """清理文件名中的非法字符"""
    name = re.sub(r'[\\/:*?"<>|]', '_', name)
    return name[:80].strip()

def main():
    if len(sys.argv) < 2:
        print("用法: python3 wechat_to_md.py <urls文件> [输出目录]")
        sys.exit(1)

    urls_file = sys.argv[1]
    out_dir = sys.argv[2] if len(sys.argv) > 2 else os.path.expanduser("~/Desktop/wechat_md")

    os.makedirs(out_dir, exist_ok=True)

    # 读取 URL 列表（跳过注释行和空行）
    urls = []
    with open(urls_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and line.startswith('http'):
                urls.append(line)

    print(f"共 {len(urls)} 篇文章，开始下载...\n")

    success = 0
    for i, url in enumerate(urls, 1):
        print(f"[{i}/{len(urls)}] {url[:60]}...", end=' ', flush=True)
        try:
            raw = fetch_page(url)
            info, body = extract_article(raw)
            title = info.get('title', '无标题')
            author = info.get('author', '')
            author_line = f"\n> 来源：{author}\n" if author else ""

            fname = sanitize_filename(title) + '.md'
            fpath = os.path.join(out_dir, fname)

            # 处理重名
            counter = 1
            while os.path.exists(fpath):
                fname = sanitize_filename(title) + f'_{counter}.md'
                fpath = os.path.join(out_dir, fname)
                counter += 1

            with open(fpath, 'w', encoding='utf-8') as f:
                f.write(f"# {title}\n")
                f.write(author_line)
                f.write(f"\n> 原文链接：{url}\n")
                f.write(f"> 下载时间：{time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write(body)

            print(f"✅ → {fname}")
            success += 1
            time.sleep(0.5)  # 礼貌间隔

        except urllib.error.HTTPError as e:
            print(f"❌ HTTP {e.code}")
        except urllib.error.URLError as e:
            print(f"❌ 网络错误: {e.reason}")
        except Exception as e:
            print(f"❌ {e}")

    print(f"\n完成！成功 {success}/{len(urls)}，保存至 {out_dir}")

if __name__ == '__main__':
    main()
