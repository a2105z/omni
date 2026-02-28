"""
FirecrawlCrawler - uses Firecrawl API for scraping.
Pluggable alternative when FIRECRAWL_API_KEY is set.
"""
from app.core.config import settings
from app.modules.crawler.interface import CrawlerInterface


class FirecrawlCrawler(CrawlerInterface):
    """Fetch and extract via Firecrawl API."""

    async def crawl(self, url: str, **kwargs) -> dict | None:
        api_key = getattr(settings, "FIRECRAWL_API_KEY", None) or ""
        if not api_key:
            return None
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    "https://api.firecrawl.dev/v1/scrape",
                    json={"url": url},
                    headers={"Authorization": f"Bearer {api_key}"},
                    timeout=30.0,
                )
                resp.raise_for_status()
                data = resp.json()
                if not data.get("success"):
                    return None
                out = data.get("data", {})
                return {
                    "url": url,
                    "html": out.get("markdown", "") or out.get("html", ""),
                    "status_code": 200,
                    "final_url": out.get("metadata", {}).get("finalUrl", url),
                    "meta": out.get("metadata", {}),
                }
        except Exception:
            return None

    async def discover_links(self, url: str, html: str) -> list[str]:
        """Links from markdown-style links."""
        import re
        from urllib.parse import urljoin, urlparse

        base = url
        # Match [text](url) and <a href="...">
        md_links = re.findall(r'\]\(([^)]+)\)', html)
        a_links = re.findall(r'href=["\']([^"\']+)["\']', html, re.I)
        links = md_links + a_links
        out = []
        for href in links:
            if href.startswith(("#", "javascript:", "mailto:")):
                continue
            full = urljoin(base, href)
            parsed = urlparse(full)
            if parsed.scheme in ("http", "https"):
                out.append(full)
        return list(dict.fromkeys(out))[:100]
