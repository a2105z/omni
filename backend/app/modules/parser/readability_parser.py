"""
ReadabilityParser - article-focused extraction using readability-lxml.
Pluggable alternative for better article content.
"""
from readability import Document

from app.modules.parser.interface import ParserInterface, ParsedDocument


class ReadabilityParser(ParserInterface):
    """Extract main article content via readability."""

    async def parse(self, html: str, url: str = "", **kwargs) -> ParsedDocument:
        doc = Document(html)
        title = doc.title() or ""
        content_html = doc.summary()
        # Strip HTML for plain text
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(content_html, "lxml")
        content = soup.get_text(separator="\n", strip=True)
        return ParsedDocument(
            url=url,
            title=title[:500],
            description="",
            content=content[:500_000],
            content_html=content_html[:500_000],
            links=[],
            meta={},
        )
