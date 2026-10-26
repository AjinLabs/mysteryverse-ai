import os
import re
from pathlib import Path
from typing import List, Dict, Any
from app.config import SUBTITLES_DIR

def format_timestamp_srt(seconds: float) -> str:
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

def format_timestamp_vtt(seconds: float) -> str:
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"

class SubtitleService:
    @staticmethod
    def create_srt_from_segments(segments: List[Dict[str, Any]], output_srt_path: str) -> str:
        """
        segments: list of {'start': float, 'end': float, 'text': str}
        """
        with open(output_srt_path, "w", encoding="utf-8") as f:
            for idx, seg in enumerate(segments, 1):
                start_str = format_timestamp_srt(seg["start"])
                end_str = format_timestamp_srt(seg["end"])
                f.write(f"{idx}\n{start_str} --> {end_str}\n{seg['text'].strip()}\n\n")
        return output_srt_path

    @staticmethod
    def create_vtt_from_segments(segments: List[Dict[str, Any]], output_vtt_path: str) -> str:
        with open(output_vtt_path, "w", encoding="utf-8") as f:
            f.write("WEBVTT\n\n")
            for idx, seg in enumerate(segments, 1):
                start_str = format_timestamp_vtt(seg["start"])
                end_str = format_timestamp_vtt(seg["end"])
                f.write(f"{idx}\n{start_str} --> {end_str}\n{seg['text'].strip()}\n\n")
        return output_vtt_path

    @staticmethod
    def create_ass_from_segments(
        segments: List[Dict[str, Any]],
        output_ass_path: str,
        is_short: bool = True
    ) -> str:
        """
        Generates Advanced SubStation Alpha (.ass) subtitles with pixel-perfect resolution,
        gold-on-dark styling, and zero overlapping with host character.
        """
        width = 1080 if is_short else 1920
        height = 1920 if is_short else 1080
        font_size = 40 if is_short else 46
        margin_v = 180 if is_short else 80
        margin_l = 60 if is_short else 100
        margin_r = 60 if is_short else 100

        def fmt_time(sec: float) -> str:
            h = int(sec // 3600)
            m = int((sec % 3600) // 60)
            s = int(sec % 60)
            cs = int((sec - int(sec)) * 100)
            return f"{h:d}:{m:02d}:{s:02d}.{cs:02d}"

        lines = [
            "[Script Info]",
            "ScriptType: v4.00+",
            f"PlayResX: {width}",
            f"PlayResY: {height}",
            "",
            "[V4+ Styles]",
            "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
            f"Style: Default,Nirmala UI,{font_size},&H0000FFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,3,1,2,{margin_l},{margin_r},{margin_v},1",
            "",
            "[Events]",
            "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
        ]
        for seg in segments:
            t_start = fmt_time(seg["start"])
            t_end = fmt_time(seg["end"])
            text = seg["text"].strip().replace("\n", "\\N")
            lines.append(f"Dialogue: 0,{t_start},{t_end},Default,,0,0,0,,{text}")

        with open(output_ass_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        return output_ass_path

    @staticmethod
    def split_script_into_timed_subtitles(full_text_mal: str, total_duration_sec: float) -> List[Dict[str, Any]]:
        """
        Splits Malayalam script into punchy, mobile-readable subtitle phrases (3-7 words each)
        and evenly distributes them across the total audio duration.
        """
        sentences = re.split(r'([.?!;।\n]+)', full_text_mal)
        phrases = []
        for s in sentences:
            s = s.strip()
            if not s or s in ".?!;।":
                continue
            words = s.split()
            # Group into chunks of ~4-6 words for great mobile shorts readability
            chunk_size = 5
            for i in range(0, len(words), chunk_size):
                chunk = " ".join(words[i:i + chunk_size])
                if chunk:
                    phrases.append(chunk)

        if not phrases:
            phrases = [full_text_mal]

        duration_per_phrase = total_duration_sec / len(phrases)
        timed_segments = []
        for i, phrase in enumerate(phrases):
            start = i * duration_per_phrase
            end = min(total_duration_sec, (i + 1) * duration_per_phrase - 0.05)
            timed_segments.append({
                "start": round(start, 2),
                "end": round(end, 2),
                "text": phrase
            })

        return timed_segments
