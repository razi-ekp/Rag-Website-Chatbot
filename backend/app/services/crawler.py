import asyncio
import re
from typing import AsyncGenerator, Dict, List, Optional, Set
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup
from loguru import logger

from app.core.config import settings


class CrawledPage:
    def __init__(self, url: str, title: str, content: str, links: List[str]):
        self.url = url
        self.title = title
        self.content = content
        self.links = links


class WebCrawler:
    def __init__(self, max_pages: Optional[int] = None):
        self.max_pages = max_pages or settings.MAX_CRAWL_PAGES
        self.visited: Set[str] = set()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (compatible; RAGChatBot/1.0)",
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "en-US,en;q=0.9",
        }

    def _normalize_url(self, url: str) -> str:
        parsed = urlparse(url)
        return parsed._replace(fragment="", query="").geturl().rstrip("/")

    def _is_same_domain(self, base_url: str, url: str) -> bool:
        return urlparse(base_url).netloc == urlparse(url).netloc

    def _is_crawlable(self, url: str) -> bool:
        skip_extensions = {
            ".pdf", ".jpg", ".jpeg", ".png", ".gif", ".svg",
            ".css", ".js", ".ico", ".zip", ".tar", ".gz",
            ".mp4", ".mp3", ".avi", ".doc", ".docx", ".xls",
        }
        path = urlparse(url).path.lower()
        return not any(path.endswith(ext) for ext in skip_extensions)

    def _extract_text(self, soup: BeautifulSoup) -> str:
        for tag in soup(["script", "style", "nav", "footer", "header", "aside", "noscript"]):
            tag.decompose()
        main_content = (
            soup.find("main") or soup.find("article")
            or soup.find(id="content") or soup.find(class_="content")
            or soup.find("body")
        )
        text = main_content.get_text(separator=" ", strip=True) if main_content else soup.get_text(separator=" ", strip=True)
        return re.sub(r"\s+", " ", text).strip()

    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        links = []
        for a_tag in soup.find_all("a", href=True):
            full_url = urljoin(base_url, a_tag["href"])
            normalized = self._normalize_url(full_url)
            if (
                self._is_same_domain(base_url, normalized)
                and self._is_crawlable(normalized)
                and normalized not in self.visited
                and normalized.startswith("http")
            ):
                links.append(normalized)
        return list(set(links))

    async def _fetch_page(self, client: httpx.AsyncClient, url: str, base_url: str) -> Optional[Dict]:
        try:
            response = await client.get(url)
            if response.status_code != 200:
                return None
            if "text/html" not in response.headers.get("content-type", ""):
                return None
            soup = BeautifulSoup(response.text, "lxml")
            title = soup.title.string.strip() if soup.title else url
            text = self._extract_text(soup)
            links = self._extract_links(soup, base_url)
            return {"url": url, "title": title, "content": text, "links": links}
        except Exception as e:
            logger.warning(f"Error fetching {url}: {e}")
            return None

    async def crawl(self, start_url: str) -> AsyncGenerator[Dict, None]:
        start_url = self._normalize_url(start_url)
        queue = [start_url]
        pages_crawled = 0
        CONCURRENT = 5  # Fetch 5 pages at once

        async with httpx.AsyncClient(
            headers=self.headers,
            timeout=15.0,
            follow_redirects=True,
            limits=httpx.Limits(max_connections=10),
        ) as client:
            while queue and pages_crawled < self.max_pages:
                # Take batch of URLs
                batch_size = min(CONCURRENT, self.max_pages - pages_crawled, len(queue))
                batch = []
                while queue and len(batch) < batch_size:
                    url = queue.pop(0)
                    if url not in self.visited:
                        self.visited.add(url)
                        batch.append(url)

                if not batch:
                    break

                # Fetch all pages in batch simultaneously
                tasks = [self._fetch_page(client, url, start_url) for url in batch]
                results = await asyncio.gather(*tasks)

                for result in results:
                    if not result:
                        continue
                    pages_crawled += 1
                    logger.info(f"Crawled [{pages_crawled}/{self.max_pages}]: {result['url']}")

                    for link in result["links"]:
                        if link not in self.visited and link not in queue:
                            queue.append(link)

                    yield {
                        "type": "page",
                        "url": result["url"],
                        "title": result["title"],
                        "content": result["content"],
                        "pages_crawled": pages_crawled,
                        "queue_size": len(queue),
                    }

        yield {
            "type": "done",
            "pages_crawled": pages_crawled,
            "total_visited": len(self.visited),
        }