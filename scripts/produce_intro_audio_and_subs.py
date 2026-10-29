"""
MysteryVerse — Official Channel Audio & Subtitle Generation (100% English)
Generates high-fidelity English neural voiceover (en-US-AndrewNeural)
and mixes a cinematic ambient soundtrack underneath.
Produces clean English subtitles with precise timing.
"""
import asyncio
import os
import sys
import subprocess
import edge_tts
from pathlib import Path
import imageio_ffmpeg

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

AUDIO_DIR = Path(r"c:\m\backend\static\audio")
SUB_DIR = Path(r"c:\m\backend\static\subtitles")
AUDIO_DIR.mkdir(parents=True, exist_ok=True)
SUB_DIR.mkdir(parents=True, exist_ok=True)

VOICE = "en-US-AndrewNeural"

SHORT_SCRIPT_EN = (
    "There are so many incredible things in this world that we don't know yet. "
    "From the deepest frontiers of space to the mysteries of ancient history, "
    "from revolutionary scientific discoveries to the secrets of the human mind! "
    "Are you ready to explore all of this? "
    "Welcome to MysteryVerse! "
    "Here, we uncover new knowledge, investigate unsolved mysteries, "
    "and challenge what we thought we knew about reality. "
    "Every video brings you a powerful new insight and an exciting question. "
    "Subscribe to MysteryVerse, and comment what topic we should explore next! "
    "Let's begin this journey of discovery together!"
)

LONG_SCRIPT_EN = (
    "In this vast and boundless universe, there are countless grand mysteries waiting for answers. "
    "When you look up at the night sky, what lies beyond those twinkling stars? "
    "From the very origins of life on Earth to the outer frontiers of the cosmos, "
    "this is an extraordinary world of awe and wonder.\n\n"
    "Hello friends! A warm and hearty welcome to everyone at MysteryVerse! "
    "Our mission is to bring you captivating scientific truths and ancient enigmas, "
    "brought to life with stunning animation. "
    "I am your host and companion, ready to guide you on this unforgettable expedition!\n\n"
    "Science is not just dry textbook formulas—it is a living, breathing everyday marvel! "
    "How do microscopic atoms and the strands of DNA truly work? "
    "How will quantum computing and artificial intelligence reshape the destiny of humanity? "
    "From futuristic robotics to groundbreaking medical revolutions, "
    "we will demystify it all with vivid, cinematic animation.\n\n"
    "Now let us voyage across the infinite expanse of outer space. "
    "From the enigmatic planets of our solar system and the majestic rings of Saturn, "
    "to hypergiant stars hundreds of times larger than our Sun, "
    "and terrifying black holes that swallow even light itself! "
    "Step by step, we will unravel the secrets of the cosmos together.\n\n"
    "Turning to history, astonishing enigmas continue to baffle the modern world. "
    "How did ancient civilizations construct the Great Pyramids thousands of years ago? "
    "What unresolved codes did the Maya and Indus Valley leave behind? "
    "We will re-examine pivotal historical turns with evidence-based scientific rigor.\n\n"
    "The human mind is an ocean even deeper than the universe itself! "
    "How do our thoughts, memories, and dreams actually spark into existence? "
    "Why do humans behave in such fascinating ways? "
    "We will explore the subconscious mind and psychological wonders through intuitive, clear breakdowns.\n\n"
    "Beyond this, you can expect jaw-dropping general knowledge, unexplained natural phenomena, "
    "bizarre creatures of the oceanic abyss, and the wonders of Earth.\n\n"
    "MysteryVerse is more than just a channel sharing facts. "
    "It is built to inspire you to ask bold questions, to see reality with fresh eyes, "
    "and to think critically without falling for misinformation or superstition.\n\n"
    "You are an essential part of this adventure of discovery! "
    "If you love exploring the unknown, hit like, share with friends, and tell us in the comments what you want to uncover next. "
    "Subscribe to MysteryVerse right now, and make sure to ring the notification bell. "
    "See you in the next exploration. Thank you, and keep seeking the truth!"
)

async def synthesize(text: str, out_path: str):
    comm = edge_tts.Communicate(text, VOICE, rate="+0%", pitch="+0Hz")
    await comm.save(out_path)
    print(f"Generated voiceover: {out_path}")

def main():
    print("Synthesizing MysteryVerse English audio...")
    raw_short = str(AUDIO_DIR / "intro_short_en_raw.mp3")
    raw_long = str(AUDIO_DIR / "intro_long_en_raw.mp3")
    asyncio.run(synthesize(SHORT_SCRIPT_EN, raw_short))
    asyncio.run(synthesize(LONG_SCRIPT_EN, raw_long))
    print("Completed English audio synthesis.")

if __name__ == "__main__":
    main()
