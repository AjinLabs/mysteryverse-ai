import os
import pytest
from app.agents.research_agent import ResearchAgent
from app.agents.deduplicator import ScriptDeduplicator
from app.agents.fact_checker import FactChecker
from app.agents.script_agent import MalayalamScriptAgent
from app.audio.subtitle_service import SubtitleService
from app.video.ffmpeg_compositor import FFmpegCompositor
from app.quality.gatekeeper import QualityGatekeeper
from app.youtube.uploader import YouTubeUploader

def test_research_discovery_and_deduplication():
    agent = ResearchAgent()
    topics = agent.discover_topics(limit=2)
    assert len(topics) >= 1
    
    # Test deduplication
    first_title = topics[0]["title"]
    first_mal = topics[0]["mal_title"]
    is_unique, sim_pct, dup_title = ScriptDeduplicator.check_topic_uniqueness(first_title, first_mal)
    assert sim_pct >= 65.0  # Should be identified as matching existing topic

def test_fact_checker_audit():
    res = FactChecker.audit_topic(
        title="Voynich Manuscript Carbon Dating",
        core_question="What century does the vellum date to?",
        sources=["https://yale.edu", "https://nature.com"],
        category="History"
    )
    assert res["status"] == "verified"
    assert res["confidence_score"] >= 80.0
    assert res["is_safe_to_produce"] is True

    # Conspiracy flag detection
    flagged_res = FactChecker.audit_topic(
        title="Secret Flat Earth Bunker",
        core_question="Is the earth flat?",
        sources=[],
        category="Conspiracy"
    )
    assert flagged_res["status"] == "flagged"
    assert flagged_res["is_safe_to_produce"] is False

def test_malayalam_script_generation():
    agent = MalayalamScriptAgent()
    sample_topic = {
        "id": "top_test_1",
        "title": "Quantum Entanglement Einstein Paradox",
        "mal_title": "ക്വാണ്ടം എൻടാംഗിൾമെന്റ്: ഐൻസ്റ്റീന്റെ രഹസ്യം",
        "category": "Science & Space",
        "format": "short"
    }
    script = agent.generate_script(sample_topic)
    assert script["id"].startswith("scr_")
    assert script["word_count"] > 10
    assert len(script["scenes"]) >= 1
    assert "ക്വാണ്ടം" in script["full_script_mal"]

def test_subtitle_timing_generator():
    text_mal = "ഭൂമി വെറും 5 സെക്കൻഡ് കറങ്ങുന്നത് നിർത്തിയാൽ എന്ത് സംഭവിക്കും? സൂപ്പർസോണിക് കൊടുങ്കാറ്റുകൾ ഉണ്ടാകും."
    segments = SubtitleService.split_script_into_timed_subtitles(text_mal, 10.0)
    assert len(segments) >= 1
    assert segments[0]["start"] == 0.0
    assert segments[-1]["end"] <= 10.0

def test_ffmpeg_compositor_validation():
    compositor = FFmpegCompositor()
    # Check test_final.mp4 that was generated earlier
    test_path = "static/videos/test_final.mp4"
    if os.path.exists(test_path):
        val = compositor.validate_video_file(test_path)
        assert val["valid"] is True
        assert val["has_video"] is True
        assert val["has_audio"] is True

def test_youtube_scheduling_kolkata_timezone():
    uploader = YouTubeUploader()
    publish_dt = uploader.calculate_next_publish_time(is_short=True)
    # Target time in IST must be 18:30
    assert publish_dt.hour == 18
    assert publish_dt.minute == 30
    assert str(publish_dt.tzinfo) == "Asia/Kolkata"
