"""
Parser Interface - abstract base for HTML-to-document extractors.
Implementations: BeautifulSoupParser, ReadabilityParser
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class ParsedDocument:
    """Structured document from parsed HTML."""

    url: str
    title: str
    description: str
    content: str  # Main text / markdown
    content_html: str | None = None
    links: list[str] | None = None
    meta: dict[str, Any] | None = None

    def to_dict(self) -> dict:
        return {
            "url": self.url,
            "title": self.title,
            "description": self.description,
            "content": self.content,
            "content_html": self.content_html,
            "links": self.links or [],
            "meta": self.meta or {},
        }


class ParserInterface(ABC):
    """Abstract parser - all implementations must satisfy this."""

    @abstractmethod
    async def parse(self, html: str, url: str = "", **kwargs: Any) -> ParsedDocument:
        """
        Convert HTML to structured document.
        """
        ...
