#!/usr/bin/env python3
"""Build the public static website into ./site.

The site is separate from book.html/PDF generation on purpose:
- book.html remains the printable artifact used by tools/build_pdf.py.
- site/ is the deployable GitHub Pages directory (and also works on Cloudflare Pages).
- the PDF stays in the GitHub repository because it is larger than Cloudflare
  Pages' 25 MiB single-asset limit.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import shutil
from pathlib import Path

import markdown
from markdown.extensions.toc import slugify_unicode

ROOT = Path(__file__).resolve().parent.parent
BOOK_MARKDOWN = ROOT / "ChatGPT橙皮书.md"
SITE_DIR = ROOT / "site"
SITE_ASSETS = SITE_DIR / "assets"
SOURCE_IMAGES = ROOT / "assets" / "images"
DEFAULT_PDF_URL = "https://raw.githubusercontent.com/bozhouDev/codex-orange-book/main/ChatGPT%E6%A9%99%E7%9A%AE%E4%B9%A6.pdf"


def strip_tags(value: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", "", value)).strip()


def read_book_meta(markdown_text: str) -> dict[str, str]:
    title_match = re.search(r"^#\s+(.+)$", markdown_text, re.M)
    version_match = re.search(r"\|\s*(v[\d.]+)\s*\|\s*(\d{4}-\d{2}-\d{2})\s*\|", markdown_text)
    return {
        "title": title_match.group(1).strip() if title_match else "ChatGPT 橙皮书",
        "version": version_match.group(1) if version_match else "v0.2.0",
        "checked_at": version_match.group(2) if version_match else "2026-07-13",
    }


def render_markdown(markdown_text: str) -> str:
    renderer = markdown.Markdown(
        extensions=["tables", "fenced_code", "sane_lists", "attr_list", "toc"],
        extension_configs={
            "toc": {
                "permalink": False,
                "slugify": slugify_unicode,
                "toc_depth": "2-4",
            }
        },
        output_format="html5",
    )
    return renderer.convert(markdown_text)


def build_toc(content_html: str) -> str:
    items: list[str] = []
    for match in re.finditer(r'<h([23]) id="([^"]+)">(.*?)</h\1>', content_html, re.S):
        level = int(match.group(1))
        anchor = match.group(2)
        label = strip_tags(match.group(3))
        if not label or label == "目录":
            continue
        class_name = "toc-link toc-link--sub" if level == 3 else "toc-link"
        items.append(f'<a class="{class_name}" href="#{anchor}">{html.escape(label)}</a>')
    return "\n".join(items)


def write_static_assets(pdf_url: str) -> None:
    SITE_ASSETS.mkdir(parents=True, exist_ok=True)
    (SITE_ASSETS / "site.css").write_text(SITE_CSS, encoding="utf-8")
    (SITE_ASSETS / "site.js").write_text(SITE_JS, encoding="utf-8")
    (SITE_DIR / "favicon.svg").write_text(FAVICON_SVG, encoding="utf-8")
    (SITE_DIR / "robots.txt").write_text("User-agent: *\nAllow: /\n", encoding="utf-8")
    (SITE_DIR / "_headers").write_text(HEADERS, encoding="utf-8")
    (SITE_DIR / "_redirects").write_text(f"/download {pdf_url} 302\n", encoding="utf-8")

    if SOURCE_IMAGES.exists():
        target_images = SITE_ASSETS / "images"
        if target_images.exists():
            shutil.rmtree(target_images)
        shutil.copytree(SOURCE_IMAGES, target_images)


def build_site(pdf_url: str) -> None:
    markdown_text = BOOK_MARKDOWN.read_text(encoding="utf-8")
    meta = read_book_meta(markdown_text)
    content_html = render_markdown(markdown_text)
    toc_html = build_toc(content_html)

    if SITE_DIR.exists():
        for path in SITE_DIR.iterdir():
            if path.name == ".git":
                continue
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()
    SITE_DIR.mkdir(exist_ok=True)

    write_static_assets(pdf_url)

    page = HTML_TEMPLATE.format(
        title=html.escape(meta["title"]),
        version=html.escape(meta["version"]),
        checked_at=html.escape(meta["checked_at"]),
        pdf_url=html.escape(pdf_url, quote=True),
        pdf_url_json=json.dumps(pdf_url, ensure_ascii=False),
        toc_html=toc_html,
        content_html=content_html,
    )
    (SITE_DIR / "index.html").write_text(page, encoding="utf-8")
    (SITE_DIR / "DEPLOY.md").write_text(DEPLOY_MD.format(pdf_url=pdf_url), encoding="utf-8")

    file_count = sum(1 for path in SITE_DIR.rglob("*") if path.is_file())
    print(f"已生成 site/，共 {file_count} 个文件")
    print(f"PDF 下载地址：{pdf_url}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the ChatGPT Orange Book website.")
    parser.add_argument(
        "--pdf-url",
        default=DEFAULT_PDF_URL,
        help="R2/public URL used by the download buttons and /download redirect.",
    )
    return parser.parse_args()


HTML_TEMPLATE = """<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <meta name="description" content="ChatGPT 橙皮书：涵盖 ChatGPT Work、Codex、Sites、浏览器与实战工作流的非官方中文指南。">
  <meta property="og:type" content="website">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="写给开发者、独立开发者和 AI 工具重度用户的 ChatGPT 使用手册。">
  <meta name="theme-color" content="#f2660a">
  <link rel="icon" href="favicon.svg" type="image/svg+xml">
  <link rel="stylesheet" href="assets/site.css">
  <script defer src="assets/site.js"></script>
</head>
<body data-pdf-url={pdf_url_json}>
  <div class="progress" aria-hidden="true"><span></span></div>

  <header class="topbar">
    <a class="brand" href="#top" aria-label="返回顶部">
      <span class="brand-mark">C</span>
      <span>ChatGPT 橙皮书</span>
    </a>
    <nav class="topnav" aria-label="主导航">
      <a href="#online-book">在线阅读</a>
      <a href="#toc">目录</a>
      <a href="/download" data-download-link>领取 PDF</a>
    </nav>
  </header>

  <main id="top">
    <section class="hero" aria-labelledby="hero-title">
      <div class="hero-copy">
        <p class="eyebrow">NON-OFFICIAL GUIDE · 持续更新版</p>
        <h1 id="hero-title">ChatGPT 橙皮书</h1>
        <p class="hero-lede">从安装、配置、核心功能到实战案例，系统梳理 ChatGPT Work、Codex、Sites、浏览器与云端工作流。</p>
        <div class="hero-actions" aria-label="主要操作">
          <a class="button button-primary" href="#online-book">开始阅读</a>
          <a class="button button-secondary" href="/download" data-download-link>领取 PDF</a>
        </div>
      </div>
      <div class="hero-side">
        <img class="hero-preview" src="assets/images/image-003-4ba99b9c0a.png" alt="ChatGPT 与 Codex 能力内容预览">
        <div class="hero-panel" aria-label="书籍信息">
          <div>
            <span class="panel-label">版本</span>
            <strong>{version}</strong>
          </div>
          <div>
            <span class="panel-label">最后校验</span>
            <strong>{checked_at}</strong>
          </div>
          <div>
            <span class="panel-label">内容范围</span>
            <strong>安装 · 配置 · 工作流 · 实战案例</strong>
          </div>
        </div>
      </div>
    </section>

    <section class="book-shell" id="online-book">
      <aside class="toc-panel" id="toc" aria-label="文章目录">
        <div class="toc-heading">目录</div>
        <nav class="toc-list">
{toc_html}
        </nav>
      </aside>

      <article class="book-content">
{content_html}
      </article>
    </section>
  </main>

  <button class="back-top" type="button" data-back-top aria-label="返回顶部">↑</button>
</body>
</html>
"""


SITE_CSS = """
:root {
  --bg: #fbfaf7;
  --paper: #ffffff;
  --ink: #171411;
  --ink-soft: #5b554d;
  --muted: #8a8177;
  --line: #e5ded5;
  --orange: #f2660a;
  --orange-deep: #c64e00;
  --teal: #0f766e;
  --teal-soft: #e4f5f2;
  --code-bg: #201b17;
  --shadow: 0 18px 60px rgba(30, 23, 16, 0.12);
  --topbar-height: 68px;
}

* { box-sizing: border-box; }

html {
  scroll-behavior: smooth;
  scroll-padding-top: calc(var(--topbar-height) + 20px);
}

body {
  margin: 0;
  background: var(--bg);
  color: var(--ink);
  font-family: "PingFang SC", "Noto Sans CJK SC", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  line-height: 1.75;
  -webkit-font-smoothing: antialiased;
}

a { color: inherit; }

.progress {
  position: fixed;
  inset: 0 0 auto;
  z-index: 30;
  height: 3px;
  background: transparent;
}

.progress span {
  display: block;
  width: 0;
  height: 100%;
  background: linear-gradient(90deg, var(--orange), var(--teal));
}

.topbar {
  position: sticky;
  top: 0;
  z-index: 20;
  height: var(--topbar-height);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  padding: 0 clamp(18px, 4vw, 56px);
  background: rgba(251, 250, 247, 0.88);
  border-bottom: 1px solid rgba(229, 222, 213, 0.85);
  backdrop-filter: blur(18px);
}

.brand {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  min-width: max-content;
  color: var(--ink);
  font-size: 15px;
  font-weight: 750;
  text-decoration: none;
}

.brand-mark {
  display: grid;
  place-items: center;
  width: 32px;
  height: 32px;
  background: var(--orange);
  color: #fff;
  border-radius: 8px;
  font-weight: 850;
}

.topnav {
  display: flex;
  align-items: center;
  gap: 10px;
}

.topnav a {
  display: inline-flex;
  align-items: center;
  min-height: 38px;
  padding: 0 14px;
  border-radius: 8px;
  color: var(--ink-soft);
  font-size: 14px;
  font-weight: 650;
  text-decoration: none;
}

.topnav a:hover {
  background: #f2ece5;
  color: var(--ink);
}

.topnav a[data-download-link] {
  background: var(--ink);
  color: #fff;
}

.hero {
  min-height: calc(88svh - var(--topbar-height));
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(280px, 380px);
  align-items: center;
  gap: clamp(28px, 6vw, 72px);
  padding: clamp(34px, 6vw, 76px) clamp(18px, 7vw, 96px) clamp(32px, 5vw, 64px);
  border-bottom: 1px solid var(--line);
}

.hero-copy {
  max-width: 860px;
}

.eyebrow {
  margin: 0 0 18px;
  color: var(--orange-deep);
  font-size: 13px;
  font-weight: 800;
  letter-spacing: 0;
}

.hero h1 {
  margin: 0;
  color: var(--ink);
  font-size: clamp(48px, 10vw, 118px);
  line-height: 0.98;
  letter-spacing: 0;
}

.hero-lede {
  max-width: 740px;
  margin: 24px 0 0;
  color: var(--ink-soft);
  font-size: clamp(18px, 2.2vw, 24px);
  line-height: 1.7;
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 34px;
}

.button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 46px;
  padding: 0 20px;
  border: 1px solid transparent;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 750;
  text-decoration: none;
}

.button-primary {
  background: var(--orange);
  color: #fff;
}

.button-secondary {
  background: var(--teal-soft);
  border-color: #b9ded8;
  color: var(--teal);
}

.hero-side {
  display: grid;
  gap: 16px;
  min-width: 0;
}

.hero-preview {
  display: block;
  width: 100%;
  aspect-ratio: 16 / 10;
  object-fit: cover;
  object-position: left top;
  border: 1px solid var(--line);
  border-radius: 8px;
  box-shadow: var(--shadow);
}

.hero-panel {
  display: grid;
  gap: 18px;
  padding: 24px;
  background: var(--paper);
  border: 1px solid var(--line);
  border-radius: 8px;
  box-shadow: var(--shadow);
}

.hero-panel div {
  display: grid;
  gap: 5px;
  padding-bottom: 17px;
  border-bottom: 1px solid var(--line);
}

.hero-panel div:last-child {
  padding-bottom: 0;
  border-bottom: 0;
}

.panel-label {
  color: var(--muted);
  font-size: 13px;
  font-weight: 700;
}

.hero-panel strong {
  color: var(--ink);
  font-size: 18px;
  line-height: 1.45;
}

.book-shell {
  display: grid;
  grid-template-columns: 280px minmax(0, 900px);
  align-items: start;
  gap: clamp(28px, 5vw, 58px);
  max-width: 1280px;
  margin: 0 auto;
  padding: 44px clamp(18px, 4vw, 40px) 96px;
}

.toc-panel {
  position: sticky;
  top: calc(var(--topbar-height) + 24px);
  max-height: calc(100svh - var(--topbar-height) - 48px);
  overflow: auto;
  padding: 18px 0;
  border-right: 1px solid var(--line);
}

.toc-heading {
  margin-bottom: 12px;
  color: var(--muted);
  font-size: 13px;
  font-weight: 800;
}

.toc-list {
  display: grid;
  gap: 2px;
  padding-right: 18px;
}

.toc-link {
  display: block;
  padding: 7px 10px;
  border-radius: 7px;
  color: var(--ink-soft);
  font-size: 13px;
  line-height: 1.45;
  text-decoration: none;
}

.toc-link--sub {
  padding-left: 20px;
  color: var(--muted);
  font-size: 12px;
}

.toc-link:hover,
.toc-link.is-active {
  background: #f1ebe3;
  color: var(--orange-deep);
}

.book-content {
  min-width: 0;
  padding: 34px clamp(18px, 4vw, 58px) 58px;
  background: var(--paper);
  border: 1px solid var(--line);
  border-radius: 8px;
}

.book-content > h1:first-child {
  margin-top: 0;
  font-size: clamp(30px, 4vw, 46px);
  line-height: 1.22;
}

.book-content h1,
.book-content h2,
.book-content h3,
.book-content h4,
.book-content h5,
.book-content h6 {
  color: var(--ink);
  line-height: 1.35;
  letter-spacing: 0;
}

.book-content h2 {
  margin: 48px 0 16px;
  padding-left: 14px;
  border-left: 5px solid var(--orange);
  font-size: clamp(24px, 3vw, 34px);
}

.book-content h3 {
  margin: 34px 0 12px;
  color: var(--orange-deep);
  font-size: clamp(20px, 2.2vw, 26px);
}

.book-content h4 {
  margin: 26px 0 10px;
  font-size: 19px;
}

.book-content h5,
.book-content h6 {
  margin: 20px 0 8px;
  color: var(--ink-soft);
  font-size: 16px;
}

.book-content p,
.book-content li {
  color: #302b25;
  font-size: 16px;
}

.book-content p {
  margin: 0 0 14px;
}

.book-content ul,
.book-content ol {
  margin: 0 0 18px;
  padding-left: 24px;
}

.book-content li + li {
  margin-top: 5px;
}

.book-content blockquote {
  margin: 20px 0;
  padding: 16px 18px;
  background: #fff7ef;
  border-left: 4px solid var(--orange);
  border-radius: 0 8px 8px 0;
}

.book-content blockquote p {
  margin: 0;
  color: var(--ink-soft);
}

.book-content table {
  width: 100%;
  margin: 18px 0 24px;
  border-collapse: collapse;
  overflow: hidden;
  font-size: 14px;
}

.book-content th,
.book-content td {
  padding: 10px 12px;
  border: 1px solid var(--line);
  text-align: left;
  vertical-align: top;
}

.book-content th {
  background: #f6efe7;
  color: var(--ink);
  font-weight: 800;
}

.book-content code {
  padding: 2px 6px;
  background: #f1ede8;
  border-radius: 5px;
  font-family: "SFMono-Regular", Consolas, "Liberation Mono", monospace;
  font-size: 0.92em;
}

.book-content pre {
  overflow: auto;
  margin: 18px 0 22px;
  padding: 18px;
  background: var(--code-bg);
  border-radius: 8px;
}

.book-content pre code {
  padding: 0;
  background: transparent;
  color: #f7efe7;
  font-size: 14px;
  line-height: 1.65;
}

.book-content a {
  color: var(--orange-deep);
  font-weight: 650;
  text-decoration-color: rgba(198, 78, 0, 0.3);
  text-underline-offset: 3px;
}

.book-content img {
  max-width: 100%;
  height: auto;
  border: 1px solid var(--line);
  border-radius: 8px;
}

.book-content p[align="center"] {
  margin: 22px 0;
  text-align: center;
}

.book-content hr {
  margin: 36px 0;
  border: 0;
  border-top: 1px solid var(--line);
}

.back-top {
  position: fixed;
  right: 18px;
  bottom: 18px;
  z-index: 25;
  display: none;
  width: 42px;
  height: 42px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: var(--paper);
  color: var(--ink);
  font-size: 20px;
  box-shadow: 0 12px 30px rgba(30, 23, 16, 0.16);
  cursor: pointer;
}

.back-top.is-visible {
  display: block;
}

@media (max-width: 980px) {
  .hero {
    min-height: auto;
    grid-template-columns: 1fr;
  }

  .hero-panel {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .hero-panel div {
    padding: 0;
    border-bottom: 0;
  }

  .book-shell {
    grid-template-columns: 1fr;
  }

  .toc-panel {
    position: static;
    max-height: none;
    padding: 16px;
    background: var(--paper);
    border: 1px solid var(--line);
    border-radius: 8px;
  }

  .toc-list {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    padding-right: 0;
  }
}

@media (max-width: 680px) {
  :root {
    --topbar-height: 62px;
  }

  .topbar {
    gap: 12px;
    padding-inline: 14px;
  }

  .brand {
    font-size: 14px;
  }

  .brand-mark {
    width: 30px;
    height: 30px;
  }

  .topnav a {
    min-height: 34px;
    padding: 0 10px;
    font-size: 13px;
  }

  .topnav a[href="#toc"] {
    display: none;
  }

  .hero {
    padding-top: 38px;
  }

  .hero-actions {
    display: grid;
    grid-template-columns: 1fr;
  }

  .button {
    width: 100%;
  }

  .hero-panel {
    grid-template-columns: 1fr;
  }

  .book-shell {
    padding-inline: 12px;
  }

  .toc-list {
    grid-template-columns: 1fr;
  }

  .book-content {
    padding: 24px 16px 40px;
  }

  .book-content table {
    display: block;
    overflow-x: auto;
    white-space: nowrap;
  }
}
"""


SITE_JS = """
(() => {
  const pdfUrl = document.body.dataset.pdfUrl;
  if (pdfUrl) {
    document.querySelectorAll('[data-download-link]').forEach((link) => {
      link.href = pdfUrl;
      link.target = '_blank';
      link.rel = 'noopener noreferrer';
    });
  }

  const progress = document.querySelector('.progress span');
  const backTop = document.querySelector('[data-back-top]');
  const tocLinks = Array.from(document.querySelectorAll('.toc-link'));
  const headings = tocLinks
    .map((link) => document.getElementById(decodeURIComponent(link.hash.slice(1))))
    .filter(Boolean);

  function updateProgress() {
    const scrollTop = window.scrollY || document.documentElement.scrollTop;
    const max = document.documentElement.scrollHeight - window.innerHeight;
    const ratio = max > 0 ? Math.min(scrollTop / max, 1) : 0;
    progress.style.width = `${ratio * 100}%`;
    backTop.classList.toggle('is-visible', scrollTop > 600);
  }

  window.addEventListener('scroll', updateProgress, { passive: true });
  window.addEventListener('resize', updateProgress);
  updateProgress();

  backTop.addEventListener('click', () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });

  if ('IntersectionObserver' in window && headings.length) {
    const byId = new Map(tocLinks.map((link) => [decodeURIComponent(link.hash.slice(1)), link]));
    const observer = new IntersectionObserver((entries) => {
      const visible = entries
        .filter((entry) => entry.isIntersecting)
        .sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top)[0];
      if (!visible) return;
      tocLinks.forEach((link) => link.classList.remove('is-active'));
      byId.get(visible.target.id)?.classList.add('is-active');
    }, { rootMargin: '-18% 0px -70% 0px', threshold: 0.01 });

    headings.forEach((heading) => observer.observe(heading));
  }
})();
"""


FAVICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <rect width="64" height="64" rx="14" fill="#f2660a"/>
  <path d="M18 45V19h18c6 0 10 4 10 9 0 4-2 7-6 8l8 9H36l-7-8h-2v8H18zm9-16h8c2 0 4-1 4-3s-2-3-4-3h-8v6z" fill="#fff"/>
</svg>
"""


HEADERS = """/*
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  Permissions-Policy: camera=(), microphone=(), geolocation=()

/assets/*
  Cache-Control: public, max-age=31536000, immutable
"""


DEPLOY_MD = """# ChatGPT 橙皮书网站发布说明

这个目录是 GitHub Pages 的发布目录，也可以直接部署到 Cloudflare Pages。

## 结构

- `index.html`：在线阅读网站入口
- `assets/site.css`：网站样式
- `assets/site.js`：阅读进度、目录高亮、返回顶部
- `assets/images/`：书稿图片资源
- `_redirects`：把 `/download` 跳转到 PDF 领取链接
- `_headers`：基础安全响应头和静态资源缓存

## GitHub Pages

仓库内的 `.github/workflows/deploy-pages.yml` 会在 `main` 分支的 `site/` 发生变化后自动部署。

公开地址：

```text
https://bozhoudev.github.io/codex-orange-book/
```

## PDF

`ChatGPT橙皮书.pdf` 当前约 38MB，超过 Cloudflare Pages 单文件 25MiB 限制，因此默认从 GitHub 仓库下载。

当前网站按钮和 `/download` 预设指向：

```text
{pdf_url}
```

如果改用 R2 或其他对象存储，重新生成网站：

```bash
python3 tools/build_site.py --pdf-url "https://你的R2域名/codex-orange-book.pdf"
```

## Cloudflare Pages

Pages 项目配置：

- Build command：留空，或填写 `python3 tools/build_site.py`
- Build output directory：`site`
- Custom domain：建议绑定 `codex.bozhouai.com`
"""


if __name__ == "__main__":
    build_site(parse_args().pdf_url)
