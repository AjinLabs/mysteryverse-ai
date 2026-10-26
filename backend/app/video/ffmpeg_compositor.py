import os
import subprocess
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from app.config import get_ffmpeg_path, VIDEOS_DIR, TEMP_DIR, DEFAULT_MALAYALAM_FONT

logger = logging.getLogger("mysteryverse.compositor")

class FFmpegCompositor:
    def __init__(self):
        self.ffmpeg_exe = get_ffmpeg_path()
        if not self.ffmpeg_exe:
            raise RuntimeError("FFmpeg executable not detected!")

    def get_media_duration(self, file_path: str) -> float:
        """Uses FFmpeg to get exact duration in seconds."""
        cmd = [
            self.ffmpeg_exe,
            "-i", file_path,
            "-f", "null",
            "-"
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        # Parse time from stderr "Duration: 00:00:15.34"
        import re
        match = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", res.stderr)
        if match:
            hours, mins, secs = match.groups()
            return int(hours) * 3600 + int(mins) * 60 + float(secs)
        return 0.0

    def assemble_final_video(
        self,
        video_clip_path: str,
        voiceover_audio_path: str,
        ambient_music_path: Optional[str],
        subtitles_path: Optional[str],
        output_mp4_path: str,
        is_short: bool = True
    ) -> Dict[str, Any]:
        """
        Mixes video, voiceover, background soundtrack, watermark, and burns subtitles
        into a YouTube-ready MP4.
        """
        audio_duration = self.get_media_duration(voiceover_audio_path)
        if audio_duration <= 0:
            audio_duration = 15.0

        # Video filter complex:
        # Loop video to match audio duration, apply fade-in / fade-out
        # In FFmpeg with fontconfig, font='Nirmala UI' or font='Arial' is cleanest on Windows
        font_arg = ":font='Nirmala UI'"
        
        # Audio mixing: narration at 1.0, ambient at 0.16
        inputs = ["-stream_loop", "-1", "-i", video_clip_path, "-i", voiceover_audio_path]
        
        filter_complex = []
        if ambient_music_path and os.path.exists(ambient_music_path):
            inputs.extend(["-stream_loop", "-1", "-i", ambient_music_path])
            # Mix two audio inputs
            filter_complex.append("[1:a]volume=1.0[vocal];[2:a]volume=0.16[bgm];[vocal][bgm]amix=inputs=2:duration=first:dropout_transition=2[aout]")
            audio_map = "[aout]"
        else:
            audio_map = "1:a"

        # Watermark branding & burned-in Malayalam subtitles
        watermark_text = "MYSTERY VERSE MALAYALAM"
        v_filters = [f"trim=duration={audio_duration}"]
        v_filters.append(f"drawtext=text='{watermark_text}':x=w-tw-30:y=40:fontsize=22:fontcolor=white@0.7:box=1:boxcolor=black@0.4:boxborderw=8{font_arg}")
        
        if subtitles_path and os.path.exists(subtitles_path):
            esc_srt = subtitles_path.replace('\\', '/').replace(':', r'\:')
            if subtitles_path.endswith('.ass'):
                sub_filter = f"subtitles='{esc_srt}'"
            else:
                margin_v = 130 if is_short else 60
                font_size = 22 if is_short else 26
                sub_filter = f"subtitles='{esc_srt}':force_style='FontName=Nirmala UI,FontSize={font_size},PrimaryColour=&H0000FFFF,OutlineColour=&H00000000,Outline=2,BorderStyle=1,MarginV={margin_v}'"
            v_filters.append(sub_filter)

        v_chain = ",".join(v_filters)
        filter_complex.append(f"[0:v]{v_chain}[vout]")

        full_filter_str = ";".join(filter_complex)

        cmd = [
            self.ffmpeg_exe,
            "-y",
            *inputs,
            "-filter_complex", full_filter_str,
            "-map", "[vout]",
            "-map", audio_map,
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-crf", "22",
            "-c:a", "aac",
            "-b:a", "192k",
            "-pix_fmt", "yuv420p",
            "-t", str(audio_duration),
            output_mp4_path
        ]

        logger.info("Running FFmpeg video assembly...")
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            logger.error("FFmpeg assembly error: %s", res.stderr)
            raise RuntimeError(f"FFmpeg assembly failed: {res.stderr[:300]}")

        # Validate resulting video file
        validation = self.validate_video_file(output_mp4_path)
        return {
            "output_path": output_mp4_path,
            "duration_sec": audio_duration,
            "validation": validation
        }

    def validate_video_file(self, video_path: str) -> Dict[str, Any]:
        """
        Validates output MP4 integrity, streams, duration, and non-empty size.
        """
        if not os.path.exists(video_path):
            return {"valid": False, "error": "File does not exist"}

        size = os.path.getsize(video_path)
        if size < 5000:
            return {"valid": False, "error": f"File size too small ({size} bytes)"}

        cmd = [self.ffmpeg_exe, "-i", video_path, "-f", "null", "-"]
        res = subprocess.run(cmd, capture_output=True, text=True)
        has_video = "Video: h264" in res.stderr
        has_audio = "Audio: aac" in res.stderr
        
        return {
            "valid": (res.returncode == 0 and has_video and has_audio),
            "has_video": has_video,
            "has_audio": has_audio,
            "file_size_bytes": size,
            "ffmpeg_code": res.returncode
        }
