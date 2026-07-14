import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


class ReaderLinkTests(unittest.TestCase):
    def test_readme_points_to_this_fork_pages_and_original_pdf_download(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("https://vink567.github.io/codex-orange-book/", readme)
        self.assertIn(
            "https://raw.githubusercontent.com/Vink567/codex-orange-book/main/ChatGPT%E6%A9%99%E7%9A%AE%E4%B9%A6.pdf",
            readme,
        )
        self.assertIn("./ChatGPT橙皮书.md", readme)

    def test_reader_page_downloads_original_pdf_and_embeds_preview_pdf(self) -> None:
        index_html = (ROOT / "index.html").read_text(encoding="utf-8")

        self.assertIn('data="./ChatGPT橙皮书.preview.pdf#view=FitH"', index_html)
        self.assertIn('href="./ChatGPT橙皮书.pdf"', index_html)
        self.assertIn('download="ChatGPT橙皮书.pdf"', index_html)
        self.assertNotIn('download="ChatGPT橙皮书.preview.pdf"', index_html)

    def test_reader_page_does_not_point_to_upstream_markdown(self) -> None:
        index_html = (ROOT / "index.html").read_text(encoding="utf-8")

        self.assertNotIn("github.com/bozhouDev/codex-orange-book/blob/main/README.md", index_html)

    def test_static_site_contains_latest_book_content(self) -> None:
        site_html = (ROOT / "site" / "index.html").read_text(encoding="utf-8")

        self.assertIn("ChatGPT 橙皮书", site_html)
        self.assertIn("v0.2.0", site_html)
        self.assertIn("Work 到底是什么", site_html)
        self.assertIn("Sites 到底是什么", site_html)
        self.assertIn("Chrome 插件", site_html)
        self.assertNotIn(">Codex 橙皮书<", site_html)


if __name__ == "__main__":
    unittest.main()
