"""
Follow-up & Session - Step 14.
Follow-up query generation, session context, session title.
"""
import json
import re
from typing import Any

from openai import AsyncOpenAI


class FollowUpService:
    """Generate follow-up queries and session titles."""

    def __init__(self, model: str = "gpt-4o-mini", num_queries: int = 5):
        self._model = model
        self._num_queries = num_queries
        self._client: AsyncOpenAI | None = None

    def _get_client(self) -> AsyncOpenAI | None:
        import os
        if not os.environ.get("OPENAI_API_KEY"):
            return None
        if self._client is None:
            self._client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        return self._client

    async def generate_follow_ups(
        self,
        query: str,
        previous_response: str,
        enhanced_queries: list[str] | None = None,
    ) -> list[str]:
        """
        Generate follow-up search queries based on original query and model response.
        Returns list of suggested follow-up queries.
        """
        client = self._get_client()
        if not client:
            return []

        enhanced = enhanced_queries or [query]
        system = (
            f"You are a helpful assistant that generates follow-up search queries. "
            f"Return a JSON object: {{\"queries\": [\"q1\", \"q2\", ...]}}. "
            f"Return exactly {self._num_queries} diverse, useful follow-up queries."
        )
        user = (
            f"Original/Enhanced queries:\n" + "\n".join(enhanced[:5]) + "\n\n"
            f"Previous model response:\n{previous_response[:4000]}"
        )

        try:
            r = await client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                response_format={"type": "json_object"},
            )
            content = r.choices[0].message.content
            if not content:
                return []
            data = json.loads(content)
            queries = data.get("queries", [])
            return [str(q) for q in queries[: self._num_queries] if q]
        except Exception:
            return []

    async def generate_session_title(self, first_query: str) -> str:
        """Generate a short session title from the first query."""
        client = self._get_client()
        if not client:
            return _truncate_query(first_query, 50)

        system = (
            "Generate a very short session title (3-8 words) for this search query. "
            "Reply with ONLY the title, no quotes or explanation."
        )
        try:
            r = await client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": first_query[:200]},
                ],
            )
            title = (r.choices[0].message.content or "").strip()
            title = re.sub(r'^["\']|["\']$', "", title)
            return _truncate_query(title or first_query, 60)
        except Exception:
            return _truncate_query(first_query, 50)


def _truncate_query(q: str, max_len: int) -> str:
    q = q.strip()[:max_len]
    if len(q) >= max_len:
        q = q.rsplit(" ", 1)[0] or q
    return q or "Search"
