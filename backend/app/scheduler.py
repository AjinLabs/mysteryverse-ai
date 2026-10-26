import os
import time
import uuid
import json
import logging
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional
from app.config import (
    settings, VIDEOS_DIR, AUDIO_DIR, SUBTITLES_DIR, THUMBNAILS_DIR,
    TARGET_SHORTS_PER_MONTH, TARGET_LONGS_PER_MONTH
)
from app.database import get_db_connection, log_event, get_setting, set_setting
from app.agents.research_agent import ResearchAgent
from app.agents.script_agent import MalayalamScriptAgent
from app.audio.tts_service import MalayalamTTSService
from app.audio.subtitle_service import SubtitleService
from app.audio.music_effects import ProceduralAudioEngine
from app.animation.blender_pipeline import AnimationPipeline
from app.video.ffmpeg_compositor import FFmpegCompositor
from app.thumbnail.thumbnail_engine import ThumbnailEngine
from app.quality.gatekeeper import QualityGatekeeper
from app.youtube.uploader import YouTubeUploader

logger = logging.getLogger("mysteryverse.scheduler")

class AutonomousScheduler:
    def __init__(self):
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self.research_agent = ResearchAgent()
        self.script_agent = MalayalamScriptAgent()
        self.tts_service = MalayalamTTSService()
        self.anim_pipeline = AnimationPipeline()
        self.compositor = FFmpegCompositor()
        self.thumbnail_engine = ThumbnailEngine()
        self.gatekeeper = QualityGatekeeper()
        self.uploader = YouTubeUploader()

    def is_killswitch_active(self) -> bool:
        return (
            os.path.exists(settings.EMERGENCY_KILLSWITCH_FILE) or
            get_setting("EMERGENCY_KILLSWITCH", "false") == "true"
        )

    def set_killswitch(self, active: bool):
        if active:
            Path(settings.EMERGENCY_KILLSWITCH_FILE).touch(exist_ok=True)
            set_setting("EMERGENCY_KILLSWITCH", "true")
            log_event("WARNING", "Scheduler", "EMERGENCY KILLSWITCH ACTIVATED - All publishing paused immediately")
        else:
            if os.path.exists(settings.EMERGENCY_KILLSWITCH_FILE):
                os.remove(settings.EMERGENCY_KILLSWITCH_FILE)
            set_setting("EMERGENCY_KILLSWITCH", "false")
            log_event("INFO", "Scheduler", "Emergency Killswitch cleared")

    def start(self):
        if self._running:
            return
        self._running = True
        set_setting("AUTONOMOUS_SCHEDULER_ACTIVE", "true")
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        log_event("INFO", "Scheduler", "Autonomous workflow scheduler started")

    def stop(self):
        self._running = False
        set_setting("AUTONOMOUS_SCHEDULER_ACTIVE", "false")
        log_event("INFO", "Scheduler", "Autonomous workflow scheduler stopped")

    def _run_loop(self):
        while self._running:
            try:
                if self.is_killswitch_active():
                    time.sleep(10)
                    continue

                # Run autonomous cycle
                self.process_autonomous_cycle()

            except Exception as e:
                logger.error("Error in scheduler execution loop: %s", e)
                log_event("ERROR", "Scheduler", f"Cycle error: {str(e)}")

            # Wait between cycles (300 seconds / 5 minutes)
            for _ in range(30):
                if not self._running:
                    break
                time.sleep(10)

    def process_autonomous_cycle(self) -> Dict[str, Any]:
        """
        Executes one complete end-to-end production pipeline iteration:
        Check quotas -> Discover -> Script -> Audio/Video Render -> Quality Gate -> Upload
        """
        if self.is_killswitch_active():
            return {"status": "paused_killswitch"}

        logger.info("Starting autonomous production cycle...")
        
        # 1. Step A: Topic Discovery (if pending topic count < 3)
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as cnt FROM topics WHERE status = 'discovered'")
        discovered_count = cursor.fetchone()["cnt"]
        
        if discovered_count < 2:
            new_topics = self.research_agent.discover_topics(limit=2)
            logger.info("Discovered %d new topics", len(new_topics))

        # 2. Step B: Scripting (for topics in 'discovered' status)
        cursor.execute("SELECT * FROM topics WHERE status = 'discovered' ORDER BY created_at ASC LIMIT 1")
        topic_to_script = cursor.fetchone()
        if topic_to_script:
            topic_dict = dict(topic_to_script)
            script_res = self.script_agent.generate_script(topic_dict)
            logger.info("Script created for topic: %s", topic_dict["title"])

        # 3. Step C: Video Production (for approved scripts without completed video job)
        cursor.execute("""
        SELECT s.*, t.mal_title, t.title, t.category, t.format, t.originality_score, t.fact_status, t.fact_confidence
        FROM scripts s
        JOIN topics t ON s.topic_id = t.id
        WHERE s.status = 'approved' AND s.id NOT IN (SELECT script_id FROM video_jobs WHERE status IN ('ready_for_upload', 'scheduled', 'uploaded'))
        LIMIT 1
        """)
        script_row = cursor.fetchone()
        
        if script_row:
            script_dict = dict(script_row)
            job_result = self.execute_video_production_pipeline(script_dict)
            conn.close()
            return job_result

        conn.close()
        return {"status": "idle", "message": "All pending jobs up to date"}

    def execute_video_production_pipeline(self, script_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes rendering, audio, subtitles, composite, quality gate, and scheduling for a script.
        """
        script_id = script_data["id"]
        topic_id = script_data["topic_id"]
        is_short = script_data.get("format", "short") == "short"
        job_id = f"job_{uuid.uuid4().hex[:10]}"
        now = datetime.now(timezone.utc).isoformat()

        logger.info("Executing video production job %s (Short: %s)...", job_id, is_short)
        
        # Insert initial video job record
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO video_jobs (
            id, script_id, topic_id, video_type, resolution,
            render_engine, status, quality_passed, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            job_id, script_id, topic_id,
            "short" if is_short else "long",
            "1080x1920" if is_short else "1920x1080",
            "procedural_motion", "rendering", False, now
        ))
        conn.commit()

        try:
            # 1. Voiceover Synthesis (Malayalam Neural TTS)
            audio_filename = f"{job_id}_voice.mp3"
            audio_path = str(AUDIO_DIR / audio_filename)
            self.tts_service.generate_speech_sync(script_data["full_script_mal"], audio_path)

            # 2. Subtitles Generation
            audio_duration = self.compositor.get_media_duration(audio_path)
            timed_segments = SubtitleService.split_script_into_timed_subtitles(script_data["full_script_mal"], audio_duration)
            srt_filename = f"{job_id}_sub.ass"
            srt_path = str(SUBTITLES_DIR / srt_filename)
            SubtitleService.create_ass_from_segments(timed_segments, srt_path, is_short=is_short)

            # 3. Ambient Soundtrack Synthesis (Procedural Royalty-Free)
            bgm_filename = f"{job_id}_bgm.wav"
            bgm_path = str(AUDIO_DIR / bgm_filename)
            ProceduralAudioEngine.generate_ambient_track(bgm_path, duration_sec=audio_duration + 2.0)

            # 4. Visual Scene Generation
            raw_clip_filename = f"{job_id}_raw.mp4"
            raw_clip_path = str(VIDEOS_DIR / raw_clip_filename)
            
            # Select first scene visual parameters
            scenes = json.loads(script_data.get("scenes_json", "[]"))
            first_scene = scenes[0] if scenes else {}
            scene_theme = first_scene.get("background_theme", "space")
            expression = first_scene.get("character_expression", "explanation")

            width = 1080 if is_short else 1920
            height = 1920 if is_short else 1080

            self.anim_pipeline.render_scene(
                output_path=raw_clip_path,
                scene_type=scene_theme,
                duration_sec=min(15.0, audio_duration),
                width=width,
                height=height,
                fps=30,
                expression=expression
            )

            # 5. FFmpeg Video Assembly & Mixing
            final_mp4_filename = f"{job_id}_final.mp4"
            final_mp4_path = str(VIDEOS_DIR / final_mp4_filename)
            
            composite_res = self.compositor.assemble_final_video(
                video_clip_path=raw_clip_path,
                voiceover_audio_path=audio_path,
                ambient_music_path=bgm_path,
                subtitles_path=srt_path,
                output_mp4_path=final_mp4_path,
                is_short=is_short
            )

            # 6. High-CTR Malayalam Thumbnail Generation
            thumb_filename = f"{job_id}_thumb.jpg"
            thumb_path = str(THUMBNAILS_DIR / thumb_filename)
            self.thumbnail_engine.generate_thumbnail(
                output_path=thumb_path,
                title_mal=script_data["mal_title"],
                category=script_data["category"],
                expression=expression,
                width=1280,
                height=720
            )

            # 7. Quality Gate Audit
            metadata = {
                "title": f"{script_data['mal_title']} | MYSTERY VERSE MALAYALAM",
                "description": f"{script_data['full_script_mal']}\n\n#Malayalam #Science #Mysteries #MysteryverseMalayalam #shorts",
                "tags": ["Malayalam", "Mystery", "Science", "Space", "Facts", "MalayalamShorts"],
                "synthetic_disclosure": True
            }
            video_job_data = {
                "id": job_id,
                "video_path": final_mp4_path,
                "thumbnail_path": thumb_path
            }
            gate_report = self.gatekeeper.audit_video_for_publishing(video_job_data, script_data, script_data, metadata)

            cursor.execute("""
            UPDATE video_jobs SET
                audio_path = ?,
                subtitles_path = ?,
                thumbnail_path = ?,
                video_path = ?,
                duration_sec = ?,
                status = ?,
                quality_passed = ?,
                quality_report_json = ?,
                completed_at = ?
            WHERE id = ?
            """, (
                audio_path, srt_path, thumb_path, final_mp4_path,
                composite_res["duration_sec"],
                "ready_for_upload" if gate_report["passed"] else "failed",
                gate_report["passed"],
                json.dumps(gate_report),
                datetime.now(timezone.utc).isoformat(),
                job_id
            ))
            conn.commit()

            # 8. Automatic Scheduling if Quality Gate Passed and Auto-Publish is enabled
            auto_publish = get_setting("AUTO_PUBLISH_ENABLED", "true") == "true"
            upload_res = None
            if gate_report["passed"] and auto_publish and not self.is_killswitch_active():
                try:
                    upload_res = self.uploader.schedule_video_upload(
                        video_job_id=job_id,
                        video_path=final_mp4_path,
                        thumbnail_path=thumb_path,
                        title=metadata["title"],
                        description=metadata["description"],
                        tags=metadata["tags"],
                        is_short=is_short
                    )
                except Exception as up_err:
                    logger.warning("Upload scheduling deferred for %s: %s", job_id, up_err)
                    log_event("WARNING", "Scheduler", f"Upload deferred for {job_id}: {str(up_err)}")

            conn.close()
            return {
                "job_id": job_id,
                "status": "success",
                "video_path": final_mp4_path,
                "thumbnail_path": thumb_path,
                "quality_passed": gate_report["passed"],
                "upload": upload_res
            }

        except Exception as e:
            logger.error("Job %s failed: %s", job_id, e)
            cursor.execute("UPDATE video_jobs SET status = 'failed', error_message = ? WHERE id = ?", (str(e), job_id))
            conn.commit()
            conn.close()
            log_event("ERROR", "Scheduler", f"Job {job_id} failed: {str(e)}")
            raise

scheduler = AutonomousScheduler()
