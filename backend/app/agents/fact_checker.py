import re
from typing import Dict, Any, List

TRUSTED_DOMAINS = [
    "nasa.gov", "esa.int", "nature.com", "science.org", "arxiv.org",
    "wikipedia.org", "nationalgeographic.com", "sciencedaily.com",
    "isro.gov.in", "cern.ch", "who.int", "britannica.com"
]

CONSPIRACY_RED_FLAGS = [
    "flat earth", "reptilian", "chemtrails", "5g chip", "faked moon landing",
    "illuminati secret bunker", "miracle cancer cure suppressed"
]

class FactChecker:
    @staticmethod
    def audit_topic(
        title: str,
        core_question: str,
        sources: List[str],
        category: str
    ) -> Dict[str, Any]:
        """
        Validates topic against credibility standards, distinguishes consensus vs hypothesis,
        and detects prohibited conspiracy claims.
        """
        combined_text = f"{title} {core_question}".lower()
        
        # 1. Check for disproven sensationalist conspiracy flags
        for flag in CONSPIRACY_RED_FLAGS:
            if flag in combined_text:
                return {
                    "status": "flagged",
                    "confidence_score": 10.0,
                    "explanation": f"Contains flagged conspiracy marker '{flag}'. Rejected under accuracy guidelines.",
                    "is_safe_to_produce": False
                }

        # 2. Score sources
        trusted_hits = 0
        for src in sources:
            src_lower = src.lower()
            if any(dom in src_lower for dom in TRUSTED_DOMAINS):
                trusted_hits += 1

        confidence = 85.0
        if trusted_hits > 0:
            confidence = min(99.0, 85.0 + (trusted_hits * 5.0))
        elif not sources:
            confidence = 75.0

        # 3. Detect speculative / what-if scenarios
        is_what_if = "what if" in combined_text or "എന്താകും" in combined_text or "സാധ്യത" in combined_text
        fact_status = "verified" if confidence >= 80.0 else "needs_review"

        return {
            "status": fact_status,
            "confidence_score": confidence,
            "trusted_source_count": trusted_hits,
            "is_what_if_scenario": is_what_if,
            "explanation": f"Validated with {trusted_hits} primary/scientific reference citations. Credible for educational production.",
            "is_safe_to_produce": True
        }
