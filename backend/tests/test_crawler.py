import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.crawler import WebCrawler


class TestWebCrawler:
    def setup_method(self):
        self.crawler = WebCrawler(max_pages=10)

    def test_normalize_url_removes_fragment(self):
        url = self.crawler._normalize_url("https://example.com/page#section")
        assert "#section" not in url

    def test_normalize_url_removes_trailing_slash(self):
        url = self.crawler._normalize_url("https://example.com/page/")
        assert not url.endswith("/")

    def test_same_domain_true(self):
        assert self.crawler._is_same_domain("https://example.com", "https://example.com/about") is True

    def test_same_domain_false(self):
        assert self.crawler._is_same_domain("https://example.com", "https://other.com/about") is False

    def test_crawlable_skips_pdf(self):
        assert self.crawler._is_crawlable("https://example.com/file.pdf") is False

    def test_crawlable_skips_image(self):
        assert self.crawler._is_crawlable("https://example.com/image.jpg") is False

    def test_crawlable_skips_css(self):
        assert self.crawler._is_crawlable("https://example.com/style.css") is False

    def test_crawlable_skips_js(self):
        assert self.crawler._is_crawlable("https://example.com/app.js") is False

    def test_crawlable_allows_html(self):
        assert self.crawler._is_crawlable("https://example.com/about") is True

    def test_crawlable_allows_root(self):
        assert self.crawler._is_crawlable("https://example.com/") is True

    def test_extract_text_removes_scripts(self):
        from bs4 import BeautifulSoup
        html = "<html><body><script>alert(1)</script><p>Hello world</p></body></html>"
        soup = BeautifulSoup(html, "lxml")
        text = self.crawler._extract_text(soup)
        assert "alert" not in text
        assert "Hello world" in text

    def test_extract_text_removes_nav(self):
        from bs4 import BeautifulSoup
        html = "<html><body><nav>Menu items</nav><main><p>Main content</p></main></body></html>"
        soup = BeautifulSoup(html, "lxml")
        text = self.crawler._extract_text(soup)
        assert "Menu items" not in text
        assert "Main content" in text

    def test_extract_links_same_domain_only(self):
        from bs4 import BeautifulSoup
        html = """<html><body>
            <a href="/about">About</a>
            <a href="https://example.com/contact">Contact</a>
            <a href="https://other.com/external">External</a>
        </body></html>"""
        soup = BeautifulSoup(html, "lxml")
        links = self.crawler._extract_links(soup, "https://example.com")
        assert all("example.com" in link for link in links)
        assert not any("other.com" in link for link in links)

    def test_max_pages_respected(self):
        crawler = WebCrawler(max_pages=5)
        assert crawler.max_pages == 5

    def test_visited_set_initialized_empty(self):
        crawler = WebCrawler()
        assert len(crawler.visited) == 0
