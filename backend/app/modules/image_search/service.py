"""
Image Search Pipeline - Step 15.
Brave image search + optional vision model for descriptions.
"""
import os
from dataclasses import dataclass

import httpx


@dataclass
class ImageResult:
    """Single image result."""

    source_number: int
    img_url: str
    title: str
    summary: str
    page_url: str | None = None


class ImageSearchService:
    """Brave image search with optional vision descriptions."""

    BRAVE_IMAGE_URL = "https://api.search.brave.com/res/v1/images/search"

    def __init__(self, max_results: int = 5, api_key: str | None = None):
        self._max_results = max_results
        self._api_key = api_key or os.environ.get("BRAVE_API_KEY")

    def is_available(self) -> bool:
        return bool(self._api_key)

    async def search(self, query: str) -> list[ImageResult]:
        """Search for images via Brave API. Returns empty list if key missing."""
        if not self._api_key:
            return []

        params = {"q": query, "count": self._max_results}
        headers = {"X-Subscription-Token": self._api_key, "Accept": "application/json"}

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                r = await client.get(self.BRAVE_IMAGE_URL, params=params, headers=headers)
                r.raise_for_status()
                data = r.json()
        except Exception:
            return []

        results = []
        for i, item in enumerate(data.get("results", [])[: self._max_results], 1):
            img_url = item.get("thumbnail", {}).get("src") or item.get("url", "")
            title = item.get("title", "Image")
            page_url = item.get("url")
            results.append(
                ImageResult(
                    source_number=i,
                    img_url=img_url,
                    title=title,
                    summary=title,
                    page_url=page_url,
                )
            )

        return results

    async def describe_with_vision(self, image_url: str) -> str:
        """
        Use vision model to describe an image. Falls back to empty string.
        Requires OPENAI_API_KEY.
        """
        key = os.environ.get("OPENAI_API_KEY")
        if not key:
            return ""

        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=key)
        try:
            r = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Briefly describe this image in one sentence."},
                            {"type": "image_url", "image_url": {"url": image_url}},
                        ],
                    }
                ],
            )
            return (r.choices[0].message.content or "").strip()
        except Exception:
            return ""
