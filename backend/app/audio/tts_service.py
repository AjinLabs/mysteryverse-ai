import asyncio
import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
import edge_tts
from app.config import (
    AUDIO_DIR,
    DEFAULT_MALE_VOICE,
    DEFAULT_FEMALE_VOICE,
    DEFAULT_VOICE_RATE,
    DEFAULT_VOICE_PITCH
)

logger = logging.getLogger("mysteryverse.tts")

class EnglishTTSService:
    """
    Zero-cost Neural English Text-to-Speech Engine with word timestamp extraction.
    Defaults to high-fidelity, energetic English voice (en-US-AndrewNeural) for host jobelessboy.
    """
    def __init__(self, voice: str = DEFAULT_MALE_VOICE):
        self.voice = voice

    async def synthesize(
        self,
        text: str,
        output_audio_path: str,
        rate: str = DEFAULT_VOICE_RATE,
        pitch: str = DEFAULT_VOICE_PITCH
    ) -> Dict[str, Any]:
        """
        Synthesizes English text to MP3 and collects word/sentence timestamps.
        """
        communicate = edge_tts.Communicate(text, self.voice, rate=rate, pitch=pitch)
        submaker = edge_tts.SubMaker()
        
        # Stream audio and collect word metadata
        with open(output_audio_path, "wb") as f:
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    f.write(chunk["data"])
                elif chunk["type"] == "WordBoundary":
                    submaker.feed(chunk)

        # Generate SubRip / WebVTT text
        srt_content = submaker.get_srt()

        return {
            "audio_path": output_audio_path,
            "voice": self.voice,
            "srt_content": srt_content,
            "file_size": os.path.getsize(output_audio_path) if os.path.exists(output_audio_path) else 0
        }

    def generate_speech_sync(self, text: str, output_audio_path: str) -> Dict[str, Any]:
        """Synchronous wrapper for FastAPI and background workers."""
        return asyncio.run(self.synthesize(text, output_audio_path))

# Backward compatibility alias
MalayalamTTSService = EnglishTTSService
