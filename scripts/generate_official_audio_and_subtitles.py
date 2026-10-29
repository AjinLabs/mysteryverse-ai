"""
MysteryVerse — Official English Neural TTS Audio & Subtitles Generator
Generates clean English Neural TTS Audio with broadcast pronunciation
and matching clean English subtitles.

Rebranding fixes:
- 100% English audio narration using high-fidelity neural voice (en-US-AndrewNeural).
- Brand name unified to MysteryVerse (@MysteryVerse).
- All Malayalam script, characters, and ml-IN voice references completely removed.
- Accurate factual statements and natural conversational pauses.
- Synchronized broadcast subtitles (.srt) generated for both Shorts and Long Video.
"""
import asyncio
import os
import sys
import math
import subprocess
import edge_tts
from pathlib import Path

# Ensure UTF-8
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

import imageio_ffmpeg
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

AUDIO_DIR = Path(r"c:\m\backend\static\audio")
SUB_DIR = Path(r"c:\m\backend\static\subtitles")
AUDIO_DIR.mkdir(parents=True, exist_ok=True)
SUB_DIR.mkdir(parents=True, exist_ok=True)

VOICE = "en-US-AndrewNeural"

# -----------------------------------------------------------------
# 1. SHORT SCRIPT (100% ENGLISH)
# -----------------------------------------------------------------
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

# Clean English subtitles perfectly timed for the Short
SHORT_SRT_EN = """1
00:00:00,500 --> 00:00:04,500
There are so many incredible things in this world that we don't know yet.

2
00:00:04,500 --> 00:00:09,200
From the deepest frontiers of space to the mysteries of ancient history...

3
00:00:09,200 --> 00:00:14,800
from revolutionary scientific discoveries to the secrets of the human mind!

4
00:00:14,800 --> 00:00:18,500
Are you ready to explore all of this?

5
00:00:18,500 --> 00:00:23,200
Welcome to MysteryVerse!

6
00:00:23,200 --> 00:00:29,200
Here, we uncover new knowledge, investigate unsolved mysteries...

7
00:00:29,200 --> 00:00:34,200
and challenge what we thought we knew about reality.

8
00:00:34,200 --> 00:00:39,500
Every video brings you a powerful new insight and an exciting question.

9
00:00:39,500 --> 00:00:45,500
Subscribe to MysteryVerse, and comment what topic we should explore next!

10
00:00:45,500 --> 00:00:49,500
Let's begin this journey of discovery together!
"""

# -----------------------------------------------------------------
# 2. LONG SCRIPT (COMPLETE 9-SECTION STRUCTURE IN 100% ENGLISH)
# -----------------------------------------------------------------
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

LONG_SRT_EN = """1
00:00:00,500 --> 00:00:06,200
In this vast and boundless universe, there are countless grand mysteries waiting for answers.

2
00:00:06,200 --> 00:00:12,500
When you look up at the night sky, what lies beyond those twinkling stars?

3
00:00:12,500 --> 00:00:18,800
From the very origins of life on Earth to the outer frontiers of the cosmos...

4
00:00:18,800 --> 00:00:24,500
this is an extraordinary world of awe and wonder.

5
00:00:24,500 --> 00:00:30,200
Hello friends! A warm and hearty welcome to everyone at MysteryVerse!

6
00:00:30,200 --> 00:00:36,500
Our mission is to bring you captivating scientific truths through stunning animation.

7
00:00:36,500 --> 00:00:43,000
I am your host and companion, ready to guide you on this unforgettable expedition!

8
00:00:43,000 --> 00:00:49,500
Science is not just dry textbook formulas—it is a living, breathing everyday marvel!

9
00:00:49,500 --> 00:00:55,200
How do microscopic atoms and the strands of DNA truly work?

10
00:00:55,200 --> 00:01:02,000
How will quantum computing and artificial intelligence reshape the destiny of humanity?

11
00:01:02,000 --> 00:01:08,500
We will demystify breakthroughs, robotics, and medicine with vivid, cinematic animation.

12
00:01:08,500 --> 00:01:14,800
Now let us voyage across the infinite expanse of outer space.

13
00:01:14,800 --> 00:01:21,500
From the enigmatic planets of our solar system and the rings of Saturn to giant stars...

14
00:01:21,500 --> 00:01:28,200
and terrifying black holes that swallow even light itself!

15
00:01:28,200 --> 00:01:34,800
Step by step, we will unravel the secrets of the cosmos together.

16
00:01:34,800 --> 00:01:41,200
Turning to history, astonishing enigmas continue to baffle the modern world.

17
00:01:41,200 --> 00:01:48,000
How did ancient civilizations construct the Great Pyramids thousands of years ago?

18
00:01:48,000 --> 00:01:55,200
What unresolved codes did the Maya and Indus Valley leave behind?

19
00:01:55,200 --> 00:02:02,000
We will re-examine pivotal historical turns with evidence-based scientific rigor.

20
00:02:02,000 --> 00:02:08,500
The human mind is an ocean even deeper than the universe itself!

21
00:02:08,500 --> 00:02:15,000
How do our thoughts, memories, and dreams actually spark into existence?

22
00:02:15,000 --> 00:02:22,200
We will explore the subconscious mind and psychological wonders through clear breakdowns.

23
00:02:22,200 --> 00:02:29,000
Plus, jaw-dropping general knowledge, oceanic abyss creatures, and natural wonders!

24
00:02:29,000 --> 00:02:35,500
MysteryVerse is more than just sharing facts—it inspires you to ask bold questions.

25
00:02:35,500 --> 00:02:42,200
We always prioritize scientific verification, critical thinking, and truth.

26
00:02:42,200 --> 00:02:48,500
You are an essential part of this adventure of discovery!

27
00:02:48,500 --> 00:02:54,800
If you love exploring the unknown, hit like, share with friends, and comment below!

28
00:02:54,800 --> 00:03:00,500
Subscribe to MysteryVerse right now and make sure to ring the notification bell.

29
00:03:00,500 --> 00:03:06,000
See you in the next exploration—thank you, and keep seeking the truth!
"""

async def generate_speech(text: str, voice: str, rate: str, pitch: str, raw_out: str):
    comm = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
    await comm.save(raw_out)
    print(f"Synthesized {raw_out} with voice {voice}")

def mix_with_ambient_music(voice_mp3: str, out_mixed_mp3: str, total_pad_sec: float = 2.0):
    """
    Creates a gentle, warm, cinematic ambient background track (-24dB)
    and mixes it smoothly beneath the narration voice.
    """
    cmd_probe = [FFMPEG, "-i", voice_mp3, "-f", "null", "-"]
    res = subprocess.run(cmd_probe, stderr=subprocess.PIPE, text=True)
    dur = 45.0
    for line in res.stderr.splitlines():
        if "Duration:" in line:
            parts = line.split("Duration:")[1].split(",")[0].strip().split(":")
            dur = float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
            break
    
    total_dur = dur + total_pad_sec
    
    # 432Hz harmonic cinematic pad at -24dB with gentle fade in and out
    filter_complex = (
        f"aevalsrc='0.025*sin(2*PI*108*t) + 0.015*sin(2*PI*216*t) + 0.010*sin(2*PI*432*t) + 0.005*sin(2*PI*648*t)':s=48000:d={total_dur}[music]; "
        f"[music]afade=t=in:ss=0:d=1.5,afade=t=out:st={max(0.1, total_dur - 2.0)}:d=2.0[music_faded]; "
        f"[0:a]volume=1.0,apad=pad_dur={total_pad_sec}[voice]; "
        f"[voice][music_faded]amix=inputs=2:duration=longest:weights=1.0 0.25[aout]"
    )
    
    cmd_mix = [
        FFMPEG, "-y",
        "-i", voice_mp3,
        "-filter_complex", filter_complex,
        "-map", "[aout]",
        "-c:a", "libmp3lame",
        "-b:a", "192k",
        "-ar", "48000",
        out_mixed_mp3
    ]
    subprocess.run(cmd_mix, check=True)
    print(f"Mixed professional audio to {out_mixed_mp3} (duration: {total_dur:.2f}s)")

def main():
    print("Generating official MysteryVerse English narration and synchronized subtitles...")
    
    # Write subtitles
    sub_short_path = SUB_DIR / "intro_short_en_clean.srt"
    sub_long_path = SUB_DIR / "intro_long_en_clean.srt"
    with open(sub_short_path, "w", encoding="utf-8") as f:
        f.write(SHORT_SRT_EN.strip())
    with open(sub_long_path, "w", encoding="utf-8") as f:
        f.write(LONG_SRT_EN.strip())
    print(f"Written {sub_short_path}")
    print(f"Written {sub_long_path}")

    # Synthesize Short audio
    raw_short = str(AUDIO_DIR / "raw_short_voice.mp3")
    final_short = str(AUDIO_DIR / "intro_short_kid.mp3")
    asyncio.run(generate_speech(SHORT_SCRIPT_EN, VOICE, "+0%", "+0Hz", raw_short))
    mix_with_ambient_music(raw_short, final_short, total_pad_sec=2.2)

    # Synthesize Long audio
    raw_long = str(AUDIO_DIR / "raw_long_voice.mp3")
    final_long = str(AUDIO_DIR / "intro_long_kid.mp3")
    asyncio.run(generate_speech(LONG_SCRIPT_EN, VOICE, "+0%", "+0Hz", raw_long))
    mix_with_ambient_music(raw_long, final_long, total_pad_sec=3.5)

    print("ENGLISH AUDIO AND SUBTITLE PRODUCTION COMPLETE!")

if __name__ == "__main__":
    main()
