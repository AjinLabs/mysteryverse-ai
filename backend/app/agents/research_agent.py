import uuid
import json
import logging
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from app.database import get_db_connection, log_event
from app.agents.deduplicator import ScriptDeduplicator
from app.agents.fact_checker import FactChecker

logger = logging.getLogger("mysteryverse.research")

# Curated catalog of authentic topic discoveries spanning all 9 channel pillars
DISCOVERY_CATALOG = [
    {
        "title": "The James Webb Space Telescope Discovers Giant Early Galaxies",
        "mal_title": "പ്രപഞ്ചത്തിന്റെ തുടക്കത്തിൽ അസാധ്യമായ ഭീമൻ ഗാലക്സികൾ! ജെയിംസ് വെബ്ബ് കണ്ടെത്തിയത് എന്ത്?",
        "core_question": "How did massive galaxies form so rapidly after the Big Bang, challenging standard cosmological models?",
        "category": "Science & Space",
        "format": "short",
        "interest_score": 96.5,
        "sources": ["https://nasa.gov/webb", "https://nature.com/articles/s41586-023-05786-2"],
        "originality_score": 94.0,
        "originality_explanation": "Focuses on the cosmological timeline paradox with Malayalam visual breakdown."
    },
    {
        "title": "The Voynich Manuscript: Cryptography or Lost Botanical Codex?",
        "mal_title": "ആർക്കും വായിക്കാൻ കഴിയാത്ത 600 വർഷം പഴക്കമുള്ള വോയ്‌നിച്ച് കയ്യെഴുത്തുപ്രതിയുടെ രഹസ്യം!",
        "core_question": "Is the 15th-century Voynich manuscript an unbreakable cipher, an unknown natural language, or an elaborate hoax?",
        "category": "Mysteries & History",
        "format": "long",
        "interest_score": 93.0,
        "sources": ["https://beinecke.library.yale.edu/collections/highlights/voynich-manuscript", "https://wikipedia.org/wiki/Voynich_manuscript"],
        "originality_score": 91.5,
        "originality_explanation": "Investigates radiocarbon dating evidence and recent statistical linguistics analysis."
    },
    {
        "title": "The Mariana Trench Challenger Deep: Life in Complete Darkness",
        "mal_title": "സമുദ്രത്തിന്റെ അഗാധതയിൽ 11 കിലോമീറ്റർ താഴെ! മരിയാന ട്രെഞ്ചിലെ അജ്ഞാത ജീവികൾ",
        "core_question": "How do organisms survive under 1,000 atmospheres of hydrostatic pressure in total darkness?",
        "category": "Ocean & Nature",
        "format": "short",
        "interest_score": 95.0,
        "sources": ["https://oceanservice.noaa.gov/facts/oceanpressure.html", "https://nationalgeographic.com/environment/article/ocean-trenches"],
        "originality_score": 92.0,
        "originality_explanation": "Highlights piezolyte protein adaptations and hydrothermal vent ecosystems in Malayalam."
    },
    {
        "title": "The Mandela Effect & False Memory Neurobiology",
        "mal_title": "മാൻഡേല ഇഫക്റ്റ്: നമ്മുടെ ഓർമ്മകൾ നമ്മളെ തന്നെ കബളിപ്പിക്കുന്നത് എങ്ങനെ?",
        "core_question": "Why do millions of unrelated people share identical vivid false memories of historical events?",
        "category": "Psychology & Behaviour",
        "format": "short",
        "interest_score": 91.0,
        "sources": ["https://psychologicalscience.org", "https://scientificamerican.com"],
        "originality_score": 90.0,
        "originality_explanation": "Explores confabulation, memory schema reconstruction, and cognitive bias mechanisms."
    },
    {
        "title": "What If Earth Stopped Spinning for Just 5 Seconds?",
        "mal_title": "ഭൂമി വെറും 5 സെക്കൻഡ് കറക്കം നിർത്തിയാൽ എന്ത് സംഭവിക്കും? ഒരു ശാസ്ത്രീയ വിശകലനം",
        "core_question": "What catastrophic kinetic and atmospheric momentum shifts would occur if planetary rotation halted instantaneously?",
        "category": "Scientific What-If",
        "format": "short",
        "interest_score": 98.0,
        "sources": ["https://nasa.gov", "https://britannica.com"],
        "originality_score": 95.0,
        "originality_explanation": "Calculates supersonic atmospheric inertia winds (1670 km/h at equator) and mega-tsunamis."
    },
    {
        "title": "Indus Valley Script: The Unsolved Linguistic Puzzle",
        "mal_title": "സിന്ധുനദീതട സംസ്കാരത്തിന്റെ ലിപി ഇന്നും വായിക്കാൻ കഴിയാത്തത് എന്തുകൊണ്ട്?",
        "core_question": "Why has the Harappan script resisted decipherment for over a century despite hundreds of seal inscriptions?",
        "category": "History & Civilisations",
        "format": "long",
        "interest_score": 92.5,
        "sources": ["https://asi.nic.in", "https://harappa.com"],
        "originality_score": 93.0,
        "originality_explanation": "Analyzes the lack of bilingual Rosetta stone equivalents and average inscription length limitations."
    },
    {
        "title": "Quantum Entanglement: Einstein's Spooky Action at a Distance",
        "mal_title": "ക്വാണ്ടം എൻടാംഗിൾമെന്റ്: പ്രകാശത്തേക്കാൾ വേഗതയിൽ പ്രപഞ്ചത്തിൽ വിവരങ്ങൾ കൈമാറാൻ കഴിയുമോ?",
        "core_question": "Does quantum non-locality violate the cosmic speed limit of special relativity?",
        "category": "Science & Technology",
        "format": "long",
        "interest_score": 94.0,
        "sources": ["https://cern.ch", "https://nobelprize.org/prizes/physics/2022/press-release"],
        "originality_score": 96.0,
        "originality_explanation": "Breaks down the 2022 Nobel Prize experiments confirming Bell inequality violations."
    },
    {
        "title": "The Wow! Signal: Interstellar Message or Cometary Resonance?",
        "mal_title": "1977-ലെ പ്രശസ്തമായ 'വാവ്!' സിഗ്നൽ: അന്യഗ്രഹ ജീവികളുടെ സന്ദേശമോ അതോ പ്രകൃതിദത്ത പ്രതിഭാസമോ?",
        "core_question": "What generated the 72-second narrowband radio burst detected by the Big Ear radio observatory in 1977?",
        "category": "Mysteries & Astronomy",
        "format": "short",
        "interest_score": 93.5,
        "sources": ["https://seti.org", "https://iopscience.iop.org"],
        "originality_score": 89.0,
        "originality_explanation": "Fairly weighs the extraterrestrial hypothesis against cometary hydrogen cloud emission theories."
    },
    {
        "title": "Bermuda Triangle: Ocean Science vs Vanishing Myth",
        "mal_title": "ബർമുഡ ട്രയാംഗിൾ: വിമാനങ്ങളും കപ്പലുകളും അപ്രത്യക്ഷമാകുന്നതിന് പിന്നിലെ യഥാർത്ഥ ശാസ്ത്രം!",
        "core_question": "What scientific oceanographic phenomena explain historical disappearances in the Sargasso Sea?",
        "category": "Mysteries & Ocean",
        "format": "short",
        "interest_score": 97.5,
        "sources": ["https://oceanservice.noaa.gov", "https://nationalgeographic.com"],
        "originality_score": 93.0,
        "originality_explanation": "Dissects rogue waves, methane hydrates, and geomagnetic compass variation in Malayalam."
    },
    {
        "title": "Antikythera Mechanism: 2000-Year-Old Ancient Analog Computer",
        "mal_title": "2000 വർഷം പഴക്കമുള്ള അത്ഭുത കമ്പ്യൂട്ടർ! ആന്റിസിതീറ മെക്കാനിസത്തിന്റെ നിഗൂഢത",
        "core_question": "How did ancient Greek engineers construct complex differential astronomical gear trains 1,000 years before Europe?",
        "category": "History & Technology",
        "format": "long",
        "interest_score": 95.0,
        "sources": ["https://nature.com", "https://smithsonianmag.com"],
        "originality_score": 94.0,
        "originality_explanation": "Analyzes X-ray micro-CT scans uncovering eclipse calculation calendar cycles."
    },
    {
        "title": "What If the Moon Disappeared Tonight?",
        "mal_title": "ഇന്ന് രാത്രി ചന്ദ്രൻ പെട്ടെന്ന് അപ്രത്യക്ഷമായാൽ നാളെ ഭൂമിയിൽ എന്ത് സംഭവിക്കും?",
        "core_question": "How does lunar gravitational stability maintain Earth's axial tilt, tides, and seasonal stability?",
        "category": "Scientific What-If",
        "format": "short",
        "interest_score": 99.0,
        "sources": ["https://nasa.gov", "https://scientificamerican.com"],
        "originality_score": 96.0,
        "originality_explanation": "Details tidal collapse, 45-degree catastrophic orbital wobble, and 6-hour daylight shifts."
    },
    {
        "title": "Sleep Paralysis: The Neuroscience Behind the Night Entity",
        "mal_title": "ഉറക്കത്തിൽ ശരീരം തളർന്നുപോകുന്ന 'ഉറക്കപ്പിശാച്' (Sleep Paralysis): യഥാർത്ഥ കാരണം!",
        "core_question": "What neurological disconnect causes consciousness to awaken during REM muscle atonia with hypnagogic visions?",
        "category": "Psychology & Brain",
        "format": "short",
        "interest_score": 96.0,
        "sources": ["https://nih.gov", "https://hopkinsmedicine.org"],
        "originality_score": 92.5,
        "originality_explanation": "Dispels superstitions with GABA/glycine motor inhibition neurobiology."
    }
]

class ResearchAgent:
    def __init__(self):
        pass

    def discover_topics(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Discovers and verifies topics for upcoming Shorts and Long-form videos.
        Prevents duplicates against existing database records.
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        discovered_topics = []

        for item in DISCOVERY_CATALOG:
            # 1. Deduplication check
            is_unique, sim_pct, dup_title = ScriptDeduplicator.check_topic_uniqueness(item["title"], item["mal_title"])
            if not is_unique:
                logger.info("Skipping topic '%s' due to high similarity (%.1f%%) with '%s'", item["title"], sim_pct, dup_title)
                continue

            # 2. Fact Check Audit
            fact_audit = FactChecker.audit_topic(
                title=item["title"],
                core_question=item["core_question"],
                sources=item["sources"],
                category=item["category"]
            )

            if not fact_audit["is_safe_to_produce"]:
                continue

            topic_id = f"top_{uuid.uuid4().hex[:10]}"
            now = datetime.now(timezone.utc).isoformat()

            cursor.execute("""
            INSERT INTO topics (
                id, title, mal_title, core_question, target_audience, category,
                format, potential_interest_score, source_references, retrieved_at,
                fact_status, fact_confidence, originality_score, originality_explanation,
                status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                topic_id,
                item["title"],
                item["mal_title"],
                item["core_question"],
                "Malayalam learners, science enthusiasts, mystery seekers",
                item["category"],
                item["format"],
                item["interest_score"],
                json.dumps(item["sources"]),
                now,
                fact_audit["status"],
                fact_audit["confidence_score"],
                item["originality_score"],
                item["originality_explanation"],
                "discovered",
                now
            ))
            conn.commit()

            discovered_topics.append({
                "id": topic_id,
                "title": item["title"],
                "mal_title": item["mal_title"],
                "category": item["category"],
                "format": item["format"],
                "interest_score": item["interest_score"],
                "fact_status": fact_audit["status"],
                "originality_score": item["originality_score"]
            })

            if len(discovered_topics) >= limit:
                break

        conn.close()
        log_event("INFO", "ResearchAgent", f"Discovered {len(discovered_topics)} new authentic topics", {"count": len(discovered_topics)})
        return discovered_topics
