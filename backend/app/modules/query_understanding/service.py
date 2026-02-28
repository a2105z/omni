"""
Query Understanding Service - Step 6.
Intent classification, query expansion, spell correction, normalization.
"""
from dataclasses import dataclass
from typing import Literal

IntentType = Literal["navigational", "informational", "transactional"]


@dataclass
class ProcessedQuery:
    """Output of query understanding."""

    original: str
    normalized: str
    tokens: list[str]
    intent: IntentType
    expanded_queries: list[str]  # Original + expansion variants for retrieval
    corrected: str | None  # Spell-corrected if different
    meta: dict


class QueryUnderstandingService:
    """Full query understanding pipeline."""

    TRANSACTIONAL_TRIGGERS = frozenset([
        "buy", "purchase", "order", "download", "install", "get", "sign up",
        "register", "subscribe", "book", "reserve", "pay", "price", "cost",
        "cheap", "free", "deal", "discount", "coupon",
    ])
    NAVIGATIONAL_TRIGGERS = frozenset([
        "login", "sign in", "facebook", "youtube", "google", "amazon",
        "twitter", "instagram", "linkedin", "github", "wikipedia",
        ".com", ".org", "website", "homepage", "official",
    ])

    def __init__(self, use_spell_check: bool = True, use_expansion: bool = True):
        self._use_spell_check = use_spell_check
        self._use_expansion = use_expansion
        self._spell_checker = None
        self._stopwords: frozenset[str] = frozenset()

    def _ensure_nltk(self) -> None:
        """Download NLTK data if needed."""
        try:
            import nltk
            try:
                nltk.data.find("tokenizers/punkt")
            except LookupError:
                nltk.download("punkt", quiet=True)
            try:
                nltk.data.find("corpora/stopwords")
            except LookupError:
                nltk.download("stopwords", quiet=True)
        except Exception:
            pass

    def _get_spell_checker(self):
        """Lazy load spell checker."""
        if self._spell_checker is not None:
            return self._spell_checker
        try:
            from spellchecker import SpellChecker
            self._spell_checker = SpellChecker()
            return self._spell_checker
        except ImportError:
            return None

    def _get_stopwords(self) -> frozenset[str]:
        if self._stopwords:
            return self._stopwords
        try:
            from nltk.corpus import stopwords
            self._stopwords = frozenset(stopwords.words("english"))
        except Exception:
            self._stopwords = frozenset(
                "a an the and or but in on at to for of with by from as is was were be been being have has had do does did will would could should may might must shall can".split()
            )
        return self._stopwords

    def normalize(self, query: str) -> str:
        """Lowercase, strip, collapse whitespace."""
        return " ".join(query.lower().strip().split())

    def tokenize(self, query: str) -> list[str]:
        """Tokenize into words (alphanumeric), optionally remove stopwords for retrieval."""
        import re
        tokens = re.findall(r"\b[a-z0-9']+\b", query.lower())
        return [t for t in tokens if t]

    def stem(self, tokens: list[str]) -> list[str]:
        """Simple stemmer - Porter if available, else identity."""
        try:
            from nltk.stem import PorterStemmer
            ps = PorterStemmer()
            return [ps.stem(t) for t in tokens]
        except Exception:
            return tokens

    def spell_correct(self, query: str) -> tuple[str, bool]:
        """Return (corrected_query, was_corrected)."""
        checker = self._get_spell_checker()
        if not checker or not self._use_spell_check:
            return query, False
        words = query.split()
        corrected = []
        changed = False
        for w in words:
            # Skip numbers and short words
            if w.isdigit() or len(w) <= 2:
                corrected.append(w)
                continue
            corr = checker.correction(w)
            if corr and corr != w:
                corrected.append(corr)
                changed = True
            else:
                corrected.append(w)
        return " ".join(corrected), changed

    def classify_intent(self, query: str) -> IntentType:
        """Classify query intent: navigational, informational, transactional."""
        tokens = set(self.tokenize(query))
        q_lower = query.lower()

        for t in self.TRANSACTIONAL_TRIGGERS:
            if t in tokens or t in q_lower:
                return "transactional"

        for t in self.NAVIGATIONAL_TRIGGERS:
            if t in tokens or t in q_lower:
                return "navigational"

        return "informational"

    def expand_query(self, query: str) -> list[str]:
        """Expand with synonyms/related terms. LLM if OPENAI_API_KEY set, else rule-based."""
        expanded = [query]
        if not self._use_expansion:
            return expanded
        llm_expanded = self._expand_via_llm(query)
        if llm_expanded:
            return llm_expanded[:5]
        synonyms = self._get_synonyms()
        tokens = self.tokenize(query)
        for token in tokens:
            if token in synonyms:
                for syn in synonyms[token][:2]:
                    variant = query.replace(token, syn)
                    if variant not in expanded:
                        expanded.append(variant)
        return expanded[:5]

    def _expand_via_llm(self, query: str) -> list[str]:
        """Optional LLM-based query expansion."""
        import os
        if not os.environ.get("OPENAI_API_KEY"):
            return []
        try:
            from openai import OpenAI
            client = OpenAI()
            r = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Given a search query, return 2-3 alternative phrasings or related queries for better web search. Output as JSON: {\"queries\": [\"q1\", \"q2\"]}. Include the original."},
                    {"role": "user", "content": query},
                ],
                max_tokens=150,
            )
            text = (r.choices[0].message.content or "").strip()
            if "```" in text:
                text = text.split("```")[1].replace("json", "").strip()
            import json
            data = json.loads(text)
            return data.get("queries", [query])[:5]
        except Exception:
            return []

    def _get_synonyms(self) -> dict[str, list[str]]:
        """Simple synonym map for common terms."""
        return {
            "best": ["top", "great", "good"],
            "good": ["great", "best", "quality"],
            "how": ["what", "way", "method"],
            "what": ["which", "how"],
            "why": ["reason", "cause"],
            "learn": ["study", "understand", "tutorial"],
            "get": ["obtain", "find", "download"],
            "make": ["create", "build", "do"],
            "use": ["utilize", "employ", "apply"],
            "free": ["gratis", "no cost"],
        }

    async def process(self, query: str) -> ProcessedQuery:
        """Full pipeline: normalize, spell-correct, tokenize, intent, expand."""
        self._ensure_nltk()
        original = query.strip()
        if not original:
            return ProcessedQuery(
                original=original,
                normalized="",
                tokens=[],
                intent="informational",
                expanded_queries=[""],
                corrected=None,
                meta={},
            )

        normalized = self.normalize(original)
        corrected, was_corrected = self.spell_correct(normalized)
        tokens = self.tokenize(corrected)
        intent = self.classify_intent(corrected)
        expanded = self.expand_query(corrected)

        return ProcessedQuery(
            original=original,
            normalized=corrected,
            tokens=tokens,
            intent=intent,
            expanded_queries=expanded,
            corrected=corrected if was_corrected else None,
            meta={"intent": intent, "num_tokens": len(tokens)},
        )
