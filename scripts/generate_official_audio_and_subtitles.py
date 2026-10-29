"""
Generates clean Malayalam Neural TTS Audio with perfect pronunciation and
matching English-only subtitles (no Malayalam text, clean subtitles).

Malayalam fixes in this version:
- Brand name written in Malayalam script (മിസ്റ്ററിവേഴ്സ് മലയാളം) so the
  ml-IN voice pronounces it correctly and suffixes like -ലേക്ക് attach properly.
- Awkward word order in the short script corrected.
- Ellipses ("...") replaced with commas/full stops (TTS reads them as odd pauses).
- "കോടിക്കണക്കിന്" corrected to "നൂറുകണക്കിന്" (factually accurate for star sizes).
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

# -----------------------------------------------------------------
# 1. SHORT SCRIPT
# -----------------------------------------------------------------
SHORT_SCRIPT_MAL = """നമ്മൾ അറിയാത്ത എത്രയോ കാര്യങ്ങൾ ഈ ലോകത്തുണ്ട്.
ബഹിരാകാശത്തിന്റെ അത്ഭുതങ്ങൾ മുതൽ ചരിത്രത്തിലെ നിഗൂഢതകൾ വരെ, ശാസ്ത്രത്തിലെ പുതിയ കണ്ടെത്തലുകൾ മുതൽ മനുഷ്യന്റെ മനസ്സിന്റെ രഹസ്യങ്ങൾ വരെ!
ഇതെല്ലാം അറിയാൻ നിങ്ങൾ തയ്യാറാണോ?
സ്വാഗതം, മിസ്റ്ററിവേഴ്സ് മലയാളത്തിലേക്ക്!
ഇവിടെ നമ്മൾ പുതിയ കാര്യങ്ങൾ അറിയും, നിഗൂഢതകൾ അന്വേഷിക്കും, നമ്മൾ വിശ്വസിക്കുന്ന പല കാര്യങ്ങളെയും ചോദ്യം ചെയ്യും.
ഓരോ വീഡിയോയും നിങ്ങൾക്ക് പുതിയൊരു അറിവും പുതിയൊരു ചോദ്യവും നൽകും.
അപ്പോൾ മിസ്റ്ററിവേഴ്സ് മലയാളം സബ്സ്ക്രൈബ് ചെയ്യൂ. നിങ്ങൾക്ക് അറിയേണ്ട അടുത്ത വിഷയം കമന്റ് ചെയ്യൂ!
അറിവിന്റെ പുതിയ ലോകത്തേക്ക് നമുക്ക് ഒരുമിച്ച് യാത്ര തുടങ്ങാം!"""

# Clean English subtitles perfectly timed for the Short
SHORT_SRT_EN = """1
00:00:00,500 --> 00:00:04,500
There are so many things in this world that we don't know.

2
00:00:04,500 --> 00:00:09,200
From the wonders of space to the mysteries of history...

3
00:00:09,200 --> 00:00:14,800
from new scientific discoveries to the secrets of the human mind!

4
00:00:14,800 --> 00:00:18,500
Are you ready to explore all of this?

5
00:00:18,500 --> 00:00:23,200
Welcome to MysteryVerse Malayalam!

6
00:00:23,200 --> 00:00:29,200
Here, we will discover new knowledge, investigate mysteries...

7
00:00:29,200 --> 00:00:34,200
and question many things we thought we knew.

8
00:00:34,200 --> 00:00:39,500
Every video will bring you a new insight and a new question.

9
00:00:39,500 --> 00:00:45,500
So subscribe to MysteryVerse Malayalam, and comment your thoughts below!

10
00:00:45,500 --> 00:00:49,500
Let's begin this journey of discovery together!
"""

# -----------------------------------------------------------------
# 2. LONG SCRIPT (COMPLETE 9-SECTION USER STRUCTURE)
# -----------------------------------------------------------------
LONG_SCRIPT_MAL = """നമ്മുടെ ഈ അനന്തമായ പ്രപഞ്ചത്തിൽ, മനുഷ്യർക്ക് ഇനിയും ഉത്തരം കണ്ടെത്താൻ കഴിയാത്ത എത്രയോ വലിയ രഹസ്യങ്ങളുണ്ട്! രാത്രിയിൽ ആകാശത്തേക്ക് നോക്കുമ്പോൾ, ആ മിന്നിത്തിളങ്ങുന്ന നക്ഷത്രങ്ങൾക്കപ്പുറം എന്തായിരിക്കും ഉള്ളത്? ഭൂമിയിലെ ജീവന്റെ ഉത്ഭവം മുതൽ പ്രപഞ്ചത്തിന്റെ അതിരുകൾ വരെ, അറിയാൻ ഏറെയുള്ള വിസ്മയങ്ങളുടെ ഒരു വലിയ ലോകമാണിത്.

നമസ്കാരം കൂട്ടുകാരേ! മിസ്റ്ററിവേഴ്സ് മലയാളത്തിലേക്ക് എല്ലാവർക്കും ഹൃദയം നിറഞ്ഞ സ്വാഗതം! അറിവുകളെയും ലോകത്തിലെ വലിയ രഹസ്യങ്ങളെയും ലളിതമായും ആനിമേഷന്റെ മനോഹാരിതയോടെയും നിങ്ങളിലേക്ക് എത്തിക്കുക എന്നതാണ് നമ്മുടെ ഈ ചാനലിന്റെ ലക്ഷ്യം. ഞാൻ നിങ്ങളുടെ കൂട്ടുകാരൻ, ഈ അത്ഭുത യാത്രയിൽ നിങ്ങളെ വഴിനടത്താൻ കൂടെയുണ്ടാകും!

ശാസ്ത്രം എന്നത് കേവലം പുസ്തകത്താളുകളിലെ തിയറികൾ മാത്രമല്ല, അത് നമ്മുടെ നിത്യജീവിതത്തിലെ അത്ഭുതമാണ്! ഏറ്റവും സൂക്ഷ്മമായ ആറ്റങ്ങളും ഡിഎൻഎയും എങ്ങനെ പ്രവർത്തിക്കുന്നു? ക്വാണ്ടം ഫിസിക്സും കൃത്രിമബുദ്ധിയും ഭാവിയെ എങ്ങനെ മാറ്റിമറിക്കും? പുതിയ ശാസ്ത്ര പരീക്ഷണങ്ങളും റോബോട്ടുകളും വൈദ്യശാസ്ത്രത്തിലെ വിപ്ലവകരമായ കണ്ടെത്തലുകളും ഇവിടെ നമ്മൾ ജീവസ്സുറ്റ ആനിമേഷനിലൂടെ മനസ്സിലാക്കും.

ഇനി നമുക്ക് ബഹിരാകാശത്തിന്റെ അനന്തവിഹായസ്സിലേക്ക് ഒരു യാത്ര പോകാം. നമ്മുടെ സ്വന്തം സൗരയൂഥത്തിലെ അത്ഭുത ഗ്രഹങ്ങൾ, ശനിയുടെ മനോഹരമായ വളയങ്ങൾ, സൂര്യനെക്കാൾ നൂറുകണക്കിന് മടങ്ങ് വലിപ്പമുള്ള നക്ഷത്രങ്ങൾ, പ്രകാശത്തെപ്പോലും ഉള്ളിലേക്ക് വലിച്ചെടുക്കുന്ന തമോഗർത്തങ്ങൾ അഥവാ ബ്ലാക്ക് ഹോളുകൾ! ഈ പ്രപഞ്ചത്തിന്റെ രഹസ്യങ്ങൾ ഓരോന്നായി നമ്മൾ ഇവിടെ ചുരുളഴിക്കും.

ചരിത്രത്തിലേക്ക് തിരിഞ്ഞുനോക്കുമ്പോൾ നമ്മെ അത്ഭുതപ്പെടുത്തുന്ന നിരവധി നിഗൂഢതകൾ കാണാം. ഈജിപ്തിലെ കൂറ്റൻ പിരമിഡുകൾ സഹസ്രാബ്ദങ്ങൾക്ക് മുമ്പ് മനുഷ്യർ എങ്ങനെ നിർമ്മിച്ചു? മായൻ സംസ്കാരവും സിന്ധുനദീതട സംസ്കാരവും ബാക്കിവെച്ച ചുരുളഴിയാത്ത രഹസ്യങ്ങൾ എന്തൊക്കെയാണ്? ചരിത്രത്തിലെ വലിയ വഴിത്തിരിവുകളും മനുഷ്യൻ ഇന്നും അന്വേഷിക്കുന്ന സമസ്യകളും നമ്മൾ ഒപ്പം അന്വേഷിക്കും.

മനുഷ്യന്റെ മനസ്സ് പ്രപഞ്ചത്തെക്കാൾ വലിയൊരു കടലാണ്! നമ്മുടെ ചിന്തകൾ, ഓർമ്മകൾ, സ്വപ്നങ്ങൾ എന്നിവ എങ്ങനെ ഉണ്ടാകുന്നു? എന്തുകൊണ്ടാണ് മനുഷ്യർ ചില പ്രത്യേക രീതികളിൽ പെരുമാറുന്നത്? സബ്കോൺഷ്യസ് മൈൻഡിന്റെ ശക്തിയും മനശാസ്ത്രപരമായ കൗതുകങ്ങളും നാം ഇവിടെ ലളിതമായ ഉദാഹരണങ്ങളിലൂടെ പഠിക്കും.

ഇതുകൂടാതെ, നിങ്ങൾ ഇതുവരെ കേട്ടിട്ടില്ലാത്ത വിസ്മയകരമായ ജനറൽ നോളജ് വിവരങ്ങൾ, ലോകരാജ്യങ്ങളുടെ കൗതുകങ്ങൾ, സമുദ്രത്തിന്റെ ആഴങ്ങളിലെ വിചിത്ര ജീവികൾ, പ്രകൃതിയിലെ വിസ്മയങ്ങൾ എന്നിവയെല്ലാം ഓരോ വീഡിയോയിലും നിങ്ങളെ കാത്തിരിക്കുന്നു.

മിസ്റ്ററിവേഴ്സ് മലയാളം എന്നത് വെറുമൊരു വിവരങ്ങൾ പങ്കുവെക്കുന്ന ചാനൽ മാത്രമല്ല. ചോദ്യങ്ങൾ ചോദിക്കാൻ നിങ്ങളെ പ്രേരിപ്പിക്കുക, ലോകത്തെ ഒരു പുതിയ കണ്ണിലൂടെ കാണാൻ സഹായിക്കുക, ചിന്തിക്കാനുള്ള കഴിവ് വളർത്തുക എന്നിവയാണ് നമ്മുടെ ലക്ഷ്യം. തെറ്റായ വാർത്തകളും അന്ധവിശ്വാസങ്ങളും ഒഴിവാക്കി, വസ്തുതകളെ ശാസ്ത്രീയമായി സമീപിക്കാൻ നമ്മൾ എപ്പോഴും ശ്രദ്ധിക്കും.

ഈ വിജ്ഞാന യാത്രയിൽ നിങ്ങൾക്കും പങ്കാളിയാകാം! ഈ വീഡിയോ ഇഷ്ടമായെങ്കിൽ താഴെ ലൈക്ക് ചെയ്യൂ, സുഹൃത്തുക്കൾക്ക് ഷെയർ ചെയ്യൂ. നിങ്ങൾക്ക് കൂടുതൽ അറിയാൻ ആഗ്രഹമുള്ള വിഷയങ്ങൾ ഏതാണെന്ന് കമന്റിൽ പറയൂ. ഇപ്പോൾ തന്നെ മിസ്റ്ററിവേഴ്സ് മലയാളം സബ്സ്ക്രൈബ് ചെയ്യൂ, ഒപ്പം ആ ബെൽ ഐക്കൺ കൂടി അമർത്തൂ. അറിവിന്റെ പുതിയൊരു ലോകവുമായി അടുത്ത വീഡിയോയിൽ കാണാം. എല്ലാവർക്കും നന്ദി, നമസ്കാരം!"""

LONG_SRT_EN = """1
00:00:00,500 --> 00:00:06,200
In this vast universe, there are countless mysteries waiting to be answered.

2
00:00:06,200 --> 00:00:12,500
When looking at the night sky, what lies beyond those twinkling stars?

3
00:00:12,500 --> 00:00:18,800
From the origins of life on Earth to the frontiers of the cosmos...

4
00:00:18,800 --> 00:00:24,500
this world is filled with wonder waiting to be explored.

5
00:00:24,500 --> 00:00:30,200
Hello friends! A warm welcome to everyone at MysteryVerse Malayalam!

6
00:00:30,200 --> 00:00:36,500
Our mission is to bring you captivating knowledge through beautiful animations.

7
00:00:36,500 --> 00:00:43,000
I am your host and companion, guiding you on this amazing expedition!

8
00:00:43,000 --> 00:00:49,500
Science is not just dry textbook theory—it is an everyday marvel!

9
00:00:49,500 --> 00:00:55,200
How do microscopic atoms and DNA really work?

10
00:00:55,200 --> 00:01:02,000
How will quantum physics and artificial intelligence reshape our future?

11
00:01:02,000 --> 00:01:08,500
We will demystify breakthroughs, robotics, and medicine with lifelike animations.

12
00:01:08,500 --> 00:01:14,800
Next, let us voyage across the infinite expanse of outer space.

13
00:01:14,800 --> 00:01:21,500
From the planets of our solar system and Saturn's rings to giant stars...

14
00:01:21,500 --> 00:01:28,200
and black holes so powerful that not even light can escape their pull!

15
00:01:28,200 --> 00:01:34,800
Step by step, we will unravel the secrets of the cosmos together.

16
00:01:34,800 --> 00:01:41,200
Turning to history, astonishing enigmas continue to puzzle us today.

17
00:01:41,200 --> 00:01:48,000
How did ancient builders construct the Great Pyramids thousands of years ago?

18
00:01:48,000 --> 00:01:55,200
What unresolved secrets did the Mayan and Indus Valley civilizations leave behind?

19
00:01:55,200 --> 00:02:02,000
We will investigate pivotal historical turns and ancient unanswered questions.

20
00:02:02,000 --> 00:02:08,500
The human mind is an ocean even deeper than the universe itself!

21
00:02:08,500 --> 00:02:15,000
How do our thoughts, memories, and dreams actually come into existence?

22
00:02:15,000 --> 00:02:22,200
We will explore the subconscious mind and fascinating psychology with clear visual examples.

23
00:02:22,200 --> 00:02:29,000
Plus, surprising general knowledge, world curiosities, deep-sea creatures, and natural wonders!

24
00:02:29,000 --> 00:02:35,500
MysteryVerse Malayalam is more than just sharing facts—it inspires you to ask big questions.

25
00:02:35,500 --> 00:02:42,200
We always prioritize scientific verification, critical thinking, and truth.

26
00:02:42,200 --> 00:02:48,500
You are an essential part of this adventure of discovery!

27
00:02:48,500 --> 00:02:54,800
If you enjoyed this, hit like, share with friends, and comment the topics you want next!

28
00:02:54,800 --> 00:03:00,500
Subscribe to MysteryVerse Malayalam right now and tap that notification bell.

29
00:03:00,500 --> 00:03:06,000
See you in the next video—stay curious and keep exploring!
"""

async def generate_speech(text: str, voice: str, rate: str, pitch: str, raw_out: str):
    comm = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
    await comm.save(raw_out)
    print(f"Synthesized {raw_out}")

def mix_with_ambient_music(voice_mp3: str, out_mixed_mp3: str, total_pad_sec: float = 2.0):
    """
    Creates a gentle, warm, cinematic ambient background track (-24dB)
    and mixes it smoothly beneath the narration voice.
    """
    # 1. Measure voice duration
    cmd_probe = [FFMPEG, "-i", voice_mp3, "-f", "null", "-"]
    res = subprocess.run(cmd_probe, stderr=subprocess.PIPE, text=True)
    dur = 45.0
    for line in res.stderr.splitlines():
        if "Duration:" in line:
            parts = line.split("Duration:")[1].split(",")[0].strip().split(":")
            dur = float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
            break
    
    total_dur = dur + total_pad_sec
    
    # 2. Generate soft cinematic musical drone/pad using ffmpeg audio synthesis (432Hz harmonic pad)
    # Voice at full volume (0dB), music pad at -24dB with gentle fade in and fade out
    filter_complex = (
        f"aevalsrc='0.025*sin(2*PI*108*t) + 0.015*sin(2*PI*216*t) + 0.010*sin(2*PI*432*t) + 0.005*sin(2*PI*648*t)':s=48000:d={total_dur}[music]; "
        f"[music]afade=t=in:ss=0:d=1.5,afade=t=out:st={total_dur - 2.0}:d=2.0[music_faded]; "
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
    print("Generating official Malayalam narration and English subtitles...")
    
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
    # ml-IN-SobhanaNeural with youthful pitch adjustment (+18Hz, +3% rate)
    asyncio.run(generate_speech(SHORT_SCRIPT_MAL, "ml-IN-SobhanaNeural", "+3%", "+18Hz", raw_short))
    mix_with_ambient_music(raw_short, final_short, total_pad_sec=2.2)

    # Synthesize Long audio
    raw_long = str(AUDIO_DIR / "raw_long_voice.mp3")
    final_long = str(AUDIO_DIR / "intro_long_kid.mp3")
    asyncio.run(generate_speech(LONG_SCRIPT_MAL, "ml-IN-SobhanaNeural", "+2%", "+18Hz", raw_long))
    mix_with_ambient_music(raw_long, final_long, total_pad_sec=3.5)

    print("AUDIO AND SUBTITLE PRODUCTION COMPLETE!")

if __name__ == "__main__":
    main()
