import asyncio
import os
import subprocess
import edge_tts
import imageio_ffmpeg
from datetime import timedelta
import re

# Refined script tailored for 52-55 seconds (YouTube Shorts 50-60s range)
# Includes all user scientific points:
# - Gradual cooling varying across the planet (no claim that oceans freeze in weeks)
# - Change in gravitational influence reaches Earth at approximately the same time as last sunlight
# - Deep underground geothermal survival
# - MysteryVerse call to action without black-hole references
SHORT_SCRIPT = (
    "Imagine waking up one morning and looking outside your window. "
    "The sky is completely dark, and the Sun has vanished! "
    "What would actually happen to our planet? "
    "Surprisingly, we wouldn't notice anything for eight minutes and twenty seconds. "
    "Because sunlight takes that long to travel ninety-three million miles to reach Earth. "
    "For eight minutes, the world would carry on completely normally. "
    "Then, the light stops arriving. "
    "Would Earth freeze instantly? No. "
    "Without sunlight, Earth's surface would gradually cool, though the rate would vary across the planet. "
    "Even stranger, the change in gravitational influence would reach Earth at approximately the same time as the last sunlight, sending our planet coasting in a straight line into deep interstellar space. "
    "Humanity could only survive by sheltering deep underground, powered by Earth's geothermal heat. "
    "Subscribe to MysteryVerse, and stay curious!"
)

async def measure():
    out_mp3 = r"c:\m\output\audio\test_short_54s.mp3"
    comm = edge_tts.Communicate(SHORT_SCRIPT, "en-US-AndrewNeural", rate="+1%", pitch="+0Hz")
    submaker = edge_tts.SubMaker()
    with open(out_mp3, "wb") as f:
        async for chunk in comm.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                submaker.feed(chunk)
    
    exe = imageio_ffmpeg.get_ffmpeg_exe()
    res = subprocess.run([exe, "-i", out_mp3], stderr=subprocess.PIPE, text=True)
    dur = 0.0
    for l in res.stderr.splitlines():
        if "Duration:" in l:
            parts = l.split("Duration:")[1].split(",")[0].strip().split(":")
            dur = float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
            print("Audio Duration:", dur, "seconds")
            break
            
    srt_text = submaker.get_srt()
    print("SRT Cues count:", len(srt_text.strip().split("\n\n")))
    with open(r"c:\m\output\subtitles\test_short_sub.srt", "w", encoding="utf-8") as f:
        f.write(srt_text)

if __name__ == "__main__":
    asyncio.run(measure())
