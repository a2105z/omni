"""
HttpxCrawler - simple HTTP crawler using httpx.
Default implementation for Phase 1.
"""
from typing import Any

import httpx
from app.core.config import settings
from app.modules.crawler.interface import CrawlerInterface, CrawlResult


class HttpxCrawler(CrawlerInterface):
    """Fetch pages via httpx."""

    def __init__(
        self,
        timeout: float = 10.0,
        user_agent: str | None = None,
    ):
        self.timeout = timeout
        self.user_agent = user_agent or settings.CRAWLER_USER_AGENT

    async def crawl(self, url: str, **kwargs: Any) -> dict | None:
        try:
            async with httpx.AsyncClient(
                timeout=self.timeout,
                follow_redirects=True,
                headers={"User-Agent": self.user_agent},
            ) as client:
                resp = await client.get(url)
                resp.raise_for_status()
                html = resp.text
                return CrawlResult(
                    url=url,
                    html=html,
                    status_code=resp.status_code,
                    final_url=str(resp.url),
                    meta={"content_type": resp.headers.get("content-type", "")},
                ).to_dict()
        except Exception:
            return None

    async def discover_links(self, url: str, html: str) -> list[str]:
        """Extract href links - basic implementation."""
        import re
        from urllib.parse import urljoin, urlparse

        base = url
        links = re.findall(r'href=["\']([^"\']+)["\']', html, re.I)
        out = []
        for href in links:
            if href.startswith(("#", "javascript:", "mailto:")):
                continue
            full = urljoin(base, href)
            parsed = urlparse(full)
            if parsed.scheme in ("http", "https"):
                out.append(full)
        return list(dict.fromkeys(out))[:100]  # dedupe, limit
