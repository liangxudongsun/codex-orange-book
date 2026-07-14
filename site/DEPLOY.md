# ChatGPT 橙皮书网站发布说明

这个目录是 Cloudflare Pages 的发布目录。

## 结构

- `index.html`：在线阅读网站入口
- `assets/site.css`：网站样式
- `assets/site.js`：阅读进度、目录高亮、返回顶部
- `assets/images/`：书稿图片资源
- `_redirects`：把 `/download` 跳转到 PDF 领取链接
- `_headers`：基础安全响应头和静态资源缓存

## PDF

`ChatGPT橙皮书.pdf` 当前约 38MB，超过 Cloudflare Pages 单文件 25MiB 限制，建议上传到 R2。

当前网站按钮和 `/download` 预设指向：

```text
https://raw.githubusercontent.com/Vink567/codex-orange-book/main/ChatGPT%E6%A9%99%E7%9A%AE%E4%B9%A6.pdf
```

建议把 PDF 上传为这个对象路径：

```text
images/codex-orange-book/codex-orange-book.pdf
```

如果 R2 URL 不同，重新生成网站：

```bash
python3 tools/build_site.py --pdf-url "https://你的R2域名/codex-orange-book.pdf"
```

## Cloudflare Pages

Pages 项目配置：

- Build command：留空，或填写 `python3 tools/build_site.py`
- Build output directory：`site`
- Custom domain：建议绑定 `codex.bozhouai.com`
