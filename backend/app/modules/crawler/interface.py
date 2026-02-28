"""
Crawler Interface - abstract base for pluggable crawlers.
Implementations: HttpxCrawler, FirecrawlCrawler, ScrapyCrawler
"""
from abc import ABC, abstractmethod
from typing import Any


class CrawlResult:
    """Raw crawl output."""

    def __init__(
        self,
        url: str,
        html: str,
        status_code: int = 200,
        final_url: str | None = None,
        meta: dict[str, Any] | None = None,
    ):
        self.url = url
        self.html = html
        self.status_code = status_code
        self.final_url = final_url or url
        self.meta = meta or {}

    def to_dict(self) -> dict:
        return {
            "url": self.url,
            "html": self.html,
            "status_code": self.status_code,
            "final_url": self.final_url,
            "meta": self.meta,
        }


class CrawlerInterface(ABC):
    """Abstract crawler - all implementations must satisfy this."""

    @abstractmethod
    async def crawl(self, url: str, **kwargs: Any) -> dict | None:
        """
        Fetch a URL and return raw content.
        Returns dict with keys: url, html, status_code, final_url, meta
        or None on failure.
        """
        ...

    @abstractmethod
    async def discover_links(self, url: str, html: str) -> list[str]:
        """Extract outgoing links from HTML for crawl queue."""
        ...
