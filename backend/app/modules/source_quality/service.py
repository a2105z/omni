"""
Source Quality Pipeline - Step 9.
Domain scoring, freshness, deduplication, diversity.
"""
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from urllib.parse import urlparse

from app.modules.retriever.hybrid import RetrievalResult


@dataclass
class ScoredResult:
    """Result with quality scores applied."""

    result: RetrievalResult
    domain_score: float
    freshness_score: float
    quality_score: float
    domain: str


# Trusted TLDs and domain patterns
TRUSTED_TLDS = frozenset({"gov", "edu", "ac"})
TRUSTED_DOMAINS = frozenset({
    "wikipedia.org", "github.com", "stackoverflow.com", "mdn.io", "developer.mozilla.org",
    "arxiv.org", "nature.com", "sciencedirect.com", "pubmed.ncbi.nlm.nih.gov",
    "reuters.com", "apnews.com", "bbc.com", "nytimes.com", "washingtonpost.com",
})
LOW_QUALITY_PATTERNS = frozenset({"blog", "wordpress", "blogspot", "medium.com", "quora.com"})


class SourceQualityService:
    """Apply source quality pipeline to retrieval results."""

    def __init__(
        self,
        max_per_domain: int = 2,
        min_domain_score: float = 0.0,
        dedup_threshold: float = 0.85,
    ):
        self._max_per_domain = max_per_domain
        self._min_domain_score = min_domain_score
        self._dedup_threshold = dedup_threshold

    @staticmethod
    def _extract_domain(url: str) -> str:
        try:
            parsed = urlparse(url)
            host = parsed.netloc or parsed.path
            host = host.lower().strip()
            if host.startswith("www."):
                host = host[4:]
            return host or "unknown"
        except Exception:
            return "unknown"

    def _domain_score(self, domain: str, mode: str = "general") -> float:
        """Score 0–1: higher = more trusted. Academic mode boosts .edu/.ac."""
        if not domain or domain == "unknown":
            return 0.5
        parts = domain.split(".")
        tld = parts[-1] if parts else ""
        if tld in TRUSTED_TLDS:
            base = 1.0
            if mode == "academic" and tld in ("edu", "ac"):
                base = 1.0  # already max; will boost quality_score later
            return base
        if domain in TRUSTED_DOMAINS:
            return 0.95
        for p in LOW_QUALITY_PATTERNS:
            if p in domain:
                return 0.2
        return 0.7  # neutral

    def _freshness_score(self, result: RetrievalResult) -> float:
        """Score 0–1 from metadata timestamp if present."""
        meta = result.metadata or {}
        ts = meta.get("timestamp") or meta.get("published") or meta.get("date")
        if not ts:
            return 0.5
        try:
            if isinstance(ts, (int, float)):
                dt = datetime.fromtimestamp(ts, tz=timezone.utc)
            elif isinstance(ts, str):
                for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%SZ"):
                    try:
                        dt = datetime.strptime(ts[:19], fmt).replace(tzinfo=timezone.utc)
                        break
                    except ValueError:
                        continue
                else:
                    return 0.5
            else:
                return 0.5
            age_days = (datetime.now(timezone.utc) - dt).days
            if age_days < 0:
                return 1.0
            if age_days < 7:
                return 0.95
            if age_days < 30:
                return 0.85
            if age_days < 365:
                return 0.7
            return max(0.3, 0.7 - age_days / 3650)
        except Exception:
            return 0.5

    def _jaccard_similarity(self, a: set, b: set) -> float:
        if not a and not b:
            return 0.0
        inter = len(a & b)
        union = len(a | b)
        return inter / union if union else 0.0

    def _tokenize(self, text: str) -> set:
        return set(re.findall(r"\b[a-z0-9]+\b", text.lower()))

    def _deduplicate(self, results: list[ScoredResult]) -> list[ScoredResult]:
        """Remove near-duplicates by Jaccard similarity on title+snippet."""
        out: list[ScoredResult] = []
        for r in results:
            tokens = self._tokenize(r.result.title + " " + r.result.snippet)
            is_dup = False
            for kept in out:
                kept_tokens = self._tokenize(kept.result.title + " " + kept.result.snippet)
                if self._jaccard_similarity(tokens, kept_tokens) >= self._dedup_threshold:
                    is_dup = True
                    break
            if not is_dup:
                out.append(r)
        return out

    def _enforce_diversity(self, results: list[ScoredResult], max_per_domain: int) -> list[ScoredResult]:
        """Limit results per domain to avoid clustering."""
        domain_count: dict[str, int] = {}
        out: list[ScoredResult] = []
        for r in results:
            d = r.domain
            domain_count[d] = domain_count.get(d, 0) + 1
            if domain_count[d] <= max_per_domain:
                out.append(r)
        return out

    def apply(
        self,
        results: list[RetrievalResult],
        apply_dedup: bool = True,
        apply_diversity: bool = True,
        mode: str = "general",
    ) -> list[RetrievalResult]:
        """
        Apply quality pipeline: domain + freshness scoring, dedup, diversity.
        Returns reordered and filtered RetrievalResults.
        """
        if not results:
            return []

        scored: list[ScoredResult] = []
        for r in results:
            domain = self._extract_domain(r.url)
            d_score = self._domain_score(domain, mode=mode)
            f_score = self._freshness_score(r)
            quality = 0.6 * d_score + 0.4 * f_score
            scored.append(ScoredResult(
                result=r,
                domain_score=d_score,
                freshness_score=f_score,
                quality_score=quality,
                domain=domain,
            ))

        # Filter by min domain score
        scored = [s for s in scored if s.domain_score >= self._min_domain_score]

        # Combine retrieval score with quality (multiplicative boost)
        # Academic mode: extra boost for .edu/.ac
        for s in scored:
            q = s.quality_score
            if mode == "academic" and s.domain.split(".")[-1] in ("edu", "ac"):
                q = min(1.0, q + 0.25)
            s.result.score *= (1.0 + 0.3 * q)

        scored.sort(key=lambda x: -x.result.score)

        if apply_dedup:
            scored = self._deduplicate(scored)
        if apply_diversity:
            scored = self._enforce_diversity(scored, self._max_per_domain)

        return [s.result for s in scored]
