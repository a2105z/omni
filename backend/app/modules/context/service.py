"""
Context Assembly - Step 11.
Aggregate top N sources into structured context with token budget.
"""
from dataclasses import dataclass


@dataclass
class TextSource:
    """Text source for context."""

    source_number: int
    url: str
    title: str
    content: str  # snippet or summary


@dataclass
class ImageSource:
    """Image source for context."""

    source_number: int
    img_url: str
    title: str
    summary: str


class ContextAssemblyService:
    """Assemble sources into token-budgeted context."""

    # Rough: 1 token ~ 4 chars for English
    CHARS_PER_TOKEN = 4

    def __init__(self, max_tokens: int = 12000):
        self._max_tokens = max_tokens

    def _estimate_tokens(self, text: str) -> int:
        return len(text) // self.CHARS_PER_TOKEN

    def assemble(
        self,
        text_sources: list[TextSource],
        image_sources: list[ImageSource] | None = None,
    ) -> tuple[str, str]:
        """
        Assemble context from sources. Truncates to fit token budget.
        Returns (source_context, image_context).
        """
        image_sources = image_sources or []
        budget = self._max_tokens
        used = 0

        sections: list[str] = []
        for s in text_sources:
            section = f"Source {s.source_number} ({s.url}): {s.title}\n{s.content}"
            tok = self._estimate_tokens(section)
            if used + tok > budget:
                remainder = (budget - used) * self.CHARS_PER_TOKEN
                if remainder > 100:
                    section = section[: int(remainder)] + "..."
                    sections.append(section)
                break
            sections.append(section)
            used += tok

        source_context = "\n\n".join(sections)

        image_sections: list[str] = []
        for img in image_sources:
            section = f"Image Source {img.source_number} ({img.img_url}): {img.title}\n{img.summary}"
            tok = self._estimate_tokens(section)
            if used + tok > budget:
                break
            image_sections.append(section)
            used += tok

        image_context = "\n\n".join(image_sections) if image_sections else ""

        return source_context, image_context
