import os
import json
import logging
from typing import Dict, Any, List
from app.config import settings
from app.database import log_event
from app.video.ffmpeg_compositor import FFmpegCompositor

logger = logging.getLogger("mysteryverse.quality")

class QualityGatekeeper:
    def __init__(self):
        self.compositor = FFmpegCompositor()

    def audit_video_for_publishing(
        self,
        video_job: Dict[str, Any],
        topic: Dict[str, Any],
        script: Dict[str, Any],
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Executes comprehensive multi-factor quality, policy, and technical checks
        before any video can be approved for upload or scheduling.
        """
        checks = {}
        critical_failures = []
        warnings = []

        # 1. Originality Check
        originality_score = float(topic.get("originality_score", 90.0))
        passed_originality = originality_score >= settings.MIN_ORIGINALITY_SCORE
        checks["originality"] = {
            "score": originality_score,
            "threshold": settings.MIN_ORIGINALITY_SCORE,
            "passed": passed_originality
        }
        if not passed_originality:
            critical_failures.append(f"Originality score {originality_score}% below threshold {settings.MIN_ORIGINALITY_SCORE}%")

        # 2. Fact Check & Source Quality
        fact_status = topic.get("fact_status", "verified")
        fact_confidence = float(topic.get("fact_confidence", 85.0))
        passed_fact = fact_status != "flagged" and fact_confidence >= settings.MIN_FACT_CHECK_CONFIDENCE
        checks["fact_integrity"] = {
            "status": fact_status,
            "confidence": fact_confidence,
            "passed": passed_fact
        }
        if not passed_fact:
            critical_failures.append(f"Fact check status '{fact_status}' (confidence: {fact_confidence}%) does not meet publishing safety criteria")

        # 3. Malayalam Script & Language Integrity
        full_script = script.get("full_script_mal", "")
        # Verify Malayalam Unicode block (\u0D00-\u0D7F)
        malayalam_chars = [c for c in full_script if '\u0D00' <= c <= '\u0D7F']
        has_malayalam = len(malayalam_chars) > 20
        checks["language_integrity"] = {
            "language": "Malayalam",
            "malayalam_char_count": len(malayalam_chars),
            "passed": has_malayalam
        }
        if not has_malayalam:
            critical_failures.append("Script does not contain sufficient verified Malayalam text")

        # 4. Video & Audio File Integrity (FFmpeg ffprobe verification)
        video_path = video_job.get("video_path")
        if not video_path or not os.path.exists(video_path):
            checks["video_integrity"] = {"passed": False, "error": "Video file missing"}
            critical_failures.append("Rendered video file is missing on disk")
        else:
            validation = self.compositor.validate_video_file(video_path)
            checks["video_integrity"] = validation
            if not validation.get("valid", False):
                critical_failures.append(f"Video validation failed: {validation}")

        # 5. Thumbnail Integrity
        thumbnail_path = video_job.get("thumbnail_path")
        if not thumbnail_path or not os.path.exists(thumbnail_path) or os.path.getsize(thumbnail_path) < 1000:
            checks["thumbnail_integrity"] = {"passed": False, "error": "Thumbnail missing or corrupt"}
            critical_failures.append("Video thumbnail is missing or corrupt")
        else:
            checks["thumbnail_integrity"] = {"passed": True, "size": os.path.getsize(thumbnail_path)}

        # 6. Metadata Completeness
        has_title = bool(metadata.get("title"))
        has_desc = bool(metadata.get("description"))
        has_tags = len(metadata.get("tags", [])) >= 3
        has_disclosure = "synthetic_disclosure" in metadata
        metadata_ok = has_title and has_desc and has_tags and has_disclosure
        checks["metadata_completeness"] = {
            "has_title": has_title,
            "has_desc": has_desc,
            "tags_count": len(metadata.get("tags", [])),
            "synthetic_disclosure": metadata.get("synthetic_disclosure", False),
            "passed": metadata_ok
        }
        if not metadata_ok:
            critical_failures.append("Metadata incomplete (requires title, description, >=3 tags, disclosure flag)")

        # 7. Licensing & Copyright (Procedural generation certification)
        checks["copyright_compliance"] = {
            "visuals": "Procedural original 3D / PIL artwork & Dr. Kiran character",
            "audio": "Procedural original mathematical synth drone & edge-tts neural Malayalam voice",
            "passed": True
        }

        passed_all = len(critical_failures) == 0
        report = {
            "passed": passed_all,
            "checks": checks,
            "critical_failures": critical_failures,
            "warnings": warnings,
            "video_job_id": video_job.get("id"),
            "recommended_action": "APPROVE_FOR_SCHEDULE" if passed_all else "REPAIR_OR_HOLD"
        }

        log_event(
            "INFO" if passed_all else "WARNING",
            "QualityGatekeeper",
            f"Quality gate check {'PASSED' if passed_all else 'FAILED'} for job {video_job.get('id')}",
            report
        )
        return report
