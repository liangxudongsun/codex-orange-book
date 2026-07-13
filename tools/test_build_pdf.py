import tempfile
import os
import sys
import types
import unittest
from pathlib import Path

from PIL import Image

sys.modules.setdefault("markdown", types.SimpleNamespace(Markdown=object))

import build_pdf


class BuildPdfAssetTests(unittest.TestCase):
    def test_build_uses_extracted_book_markdown_as_source(self) -> None:
        self.assertEqual(build_pdf.BOOK_MARKDOWN.name, "ChatGPT橙皮书.md")

    def test_build_outputs_download_and_preview_pdfs(self) -> None:
        self.assertEqual(build_pdf.OUTPUT_PDF.name, "ChatGPT橙皮书.pdf")
        self.assertEqual(build_pdf.OUTPUT_PREVIEW_PDF.name, "ChatGPT橙皮书.preview.pdf")

    def test_pdf_source_excludes_reading_entry_section(self) -> None:
        source = """# Codex 橙皮书

开头介绍。

## 阅读入口

- [在线阅读](https://vink567.github.io/codex-orange-book/)
- [下载 PDF](https://raw.githubusercontent.com/Vink567/codex-orange-book/main/ChatGPT%E6%A9%99%E7%9A%AE%E4%B9%A6.pdf)
- [Markdown 原文](https://github.com/Vink567/codex-orange-book/blob/main/README.md)

> GitHub 文件页可能无法稳定预览较大的 PDF。

## 目录

- 第一篇
"""

        prepared = build_pdf.prepare_book_markdown_for_pdf(source)

        self.assertIn("# Codex 橙皮书", prepared)
        self.assertIn("## 目录", prepared)
        self.assertIn("- 第一篇", prepared)
        self.assertNotIn("## 阅读入口", prepared)
        self.assertNotIn("在线阅读", prepared)
        self.assertNotIn("下载 PDF", prepared)
        self.assertNotIn("Markdown 原文", prepared)
        self.assertNotIn("GitHub 文件页可能无法稳定预览", prepared)

    def test_resolve_chrome_prefers_env_path(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            fake_chrome = Path(raw_tmp) / "chrome"
            fake_chrome.write_text("", encoding="utf-8")
            old_value = os.environ.get("CHROME_PATH")
            os.environ["CHROME_PATH"] = str(fake_chrome)
            try:
                self.assertEqual(build_pdf.resolve_chrome(), fake_chrome)
            finally:
                if old_value is None:
                    os.environ.pop("CHROME_PATH", None)
                else:
                    os.environ["CHROME_PATH"] = old_value

    def test_prepare_pdf_assets_rewrites_local_png_to_optimized_jpeg(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            tmp_path = Path(raw_tmp)
            source = tmp_path / "assets" / "images" / "sample.png"
            source.parent.mkdir(parents=True)
            Image.new("RGB", (2000, 1000), "#f2660a").save(source)

            html = '<p><img src="assets/images/sample.png" alt="sample" width="860"></p>'

            optimized = build_pdf.prepare_pdf_assets(html, tmp_path)

            expected = tmp_path / ".cache" / "pdf-assets" / "assets" / "images" / "sample.jpg"
            self.assertTrue(expected.exists())
            self.assertIn('src=".cache/pdf-assets/assets/images/sample.jpg"', optimized)

            with Image.open(expected) as image:
                self.assertEqual(image.format, "JPEG")
                self.assertLessEqual(image.width, build_pdf.PDF_IMAGE_MAX_WIDTH)
                self.assertLess(image.height, 1000)


if __name__ == "__main__":
    unittest.main()
