"""
BeautifulSoupParser - extract content using BeautifulSoup.
Default implementation for Phase 1.
"""
from bs4 import BeautifulSoup

from app.modules.parser.interface import ParserInterface, ParsedDocument


class BeautifulSoupParser(ParserInterface):
    """Parse HTML with BeautifulSoup."""

    async def parse(self, html: str, url: str = "", **kwargs) -> ParsedDocument:
        soup = BeautifulSoup(html, "lxml")
        # Remove script/style
        for tag in soup(["script", "style"]):
            tag.decompose()
        text = soup.get_text(separator="\n", strip=True)
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        content = "\n\n".join(lines)

        title = ""
        if soup.title:
            title = soup.title.string or ""
        elif soup.find("h1"):
            title = soup.find("h1").get_text(strip=True)

        desc = ""
        meta = soup.find("meta", attrs={"name": "description"}) or soup.find(
            "meta", attrs={"property": "og:description"}
        )
        if meta and meta.get("content"):
            desc = meta["content"]

        links = []
        for a in soup.find_all("a", href=True)[:200]:
            href = a["href"]
            if href.startswith(("#", "javascript:", "mailto:")):
                continue
            links.append(href)

        return ParsedDocument(
            url=url,
            title=title[:500] if title else "",
            description=desc[:1000] if desc else "",
            content=content[:500_000],
            content_html=None,
            links=links,
            meta={},
        )
