"""
Citation-Aware Synthesizer - Step 12.
Streaming LLM response with strict citation format [1](url).
"""
from typing import AsyncIterator

from openai import AsyncOpenAI

from app.modules.focus_modes.config import get_focus_mode_prompt


class SynthesisService:
    """Stream citation-aware answers from sources."""

    def __init__(self, model: str = "gpt-4o-mini"):
        self._model = model
        self._client: AsyncOpenAI | None = None

    def _get_client(self) -> AsyncOpenAI:
        if self._client is None:
            from openai import AsyncOpenAI
            import os
            key = os.environ.get("OPENAI_API_KEY")
            if not key:
                raise RuntimeError("OPENAI_API_KEY required for synthesis")
            self._client = AsyncOpenAI(api_key=key)
        return self._client

    async def synthesize_stream(
        self,
        query: str,
        source_context: str,
        image_context: str,
        mode: str = "general",
    ) -> AsyncIterator[str]:
        """Stream answer chunks. Yields text fragments."""
        if not source_context and not image_context:
            yield "I don't have any sources to answer this question. Please try a different query or ensure results are indexed."
            return

        system = get_focus_mode_prompt(mode) + """

**Image Usage:** When relevant, embed images using Markdown: ![title](url). Only use image URLs from the provided image sources."""

        user_content = f"Question: {query}"
        if source_context:
            user_content += f"\n\nSources:\n{source_context}"
        if image_context:
            user_content += f"\n\nImages:\n{image_context}"

        client = self._get_client()
        stream = await client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user_content},
            ],
            stream=True,
        )

        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
