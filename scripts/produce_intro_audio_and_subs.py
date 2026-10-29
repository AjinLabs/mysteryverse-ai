"""
MysteryVerse Malayalam — Audio & Subtitle Generation
Uses the EXACT approved user scripts verbatim with zero changes.
Generates ml-IN-SobhanaNeural voiceover with youthful kid pitch (+18Hz)
and mixes cinematic ambient soundtrack underneath.
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

# =====================================================================
# EXACT APPROVED SHORT SCRIPT (VERBATIM FROM USER)
# =====================================================================
SHORT_SCRIPT_MAL = """നമസ്കാരം കൂട്ടുകാരേ!
ഈ ലോകത്ത് നമ്മൾ ഇതുവരെ അറിയാത്ത എത്രയോ കാര്യങ്ങളുണ്ട്. ബഹിരാകാശത്തിന്റെ അത്ഭുതങ്ങൾ, ചരിത്രത്തിലെ നിഗൂഢതകൾ, ശാസ്ത്രത്തിലെ വിസ്മയങ്ങൾ, മനുഷ്യന്റെ മനസ്സിലെ രഹസ്യങ്ങൾ…
ഇവയെല്ലാം അറിയാൻ നിങ്ങൾക്ക് താൽപ്പര്യമുണ്ടോ?
എങ്കിൽ, സ്വാഗതം… മിസ്റ്ററി വേഴ്സ് മലയാളത്തിലേക്ക്!
ഇവിടെ നമ്മൾ ബഹിരാകാശത്തെക്കുറിച്ചും ശാസ്ത്രത്തെക്കുറിച്ചും രസകരമായ വസ്തുതകളെക്കുറിച്ചും ചരിത്രത്തെക്കുറിച്ചും അറിയും.
നിഗൂഢമായ സംഭവങ്ങൾ അന്വേഷിക്കും. മനുഷ്യന്റെ ചിന്തകളും പെരുമാറ്റവും മനസ്സിലാക്കാൻ ശ്രമിക്കും. നമ്മൾ സാധാരണയായി ചോദിക്കാത്ത ചോദ്യങ്ങൾക്കും ഉത്തരം തേടും.
ഓരോ വീഡിയോയും പുതിയൊരു അറിവിലേക്കുള്ള യാത്രയായിരിക്കും.
അപ്പോൾ, ഈ അറിവിന്റെ യാത്രയിൽ ഞങ്ങളോടൊപ്പം ചേരൂ. ചാനൽ സബ്സ്ക്രൈബ് ചെയ്യൂ. നിങ്ങൾ അടുത്തതായി അറിയാൻ ആഗ്രഹിക്കുന്ന വിഷയം കമന്റിൽ പറയൂ.
നമുക്ക് ഒരുമിച്ച് പുതിയ കാര്യങ്ങൾ കണ്ടെത്താം!"""

# =====================================================================
# EXACT APPROVED LONG SCRIPT (VERBATIM FROM USER)
# =====================================================================
LONG_SCRIPT_MAL = """നമസ്കാരം കൂട്ടുകാരേ!
നിങ്ങൾ എപ്പോഴെങ്കിലും രാത്രി ആകാശത്തേക്ക് നോക്കി ചിന്തിച്ചിട്ടുണ്ടോ? ഈ വിശാലമായ പ്രപഞ്ചത്തിൽ നമുക്ക് അറിയാത്ത എത്ര കാര്യങ്ങളുണ്ടാകും? ആയിരക്കണക്കിന് വർഷങ്ങൾക്കുമുമ്പ് നടന്ന സംഭവങ്ങളിൽ ഇനിയും കണ്ടെത്താത്ത രഹസ്യങ്ങൾ ഉണ്ടാകുമോ? നമ്മുടെ സ്വന്തം മനസ്സ് എങ്ങനെയാണ് പ്രവർത്തിക്കുന്നത്?
ഇത്തരം ചോദ്യങ്ങൾ നിങ്ങളെയും ചിന്തിപ്പിക്കാറുണ്ടെങ്കിൽ, നിങ്ങൾ എത്തിയിരിക്കുന്നത് ശരിയായ സ്ഥലത്താണ്.
സ്വാഗതം… മിസ്റ്ററി വേഴ്സ് മലയാളത്തിലേക്ക്!
ഇത് അറിവിന്റെയും ശാസ്ത്രത്തിന്റെയും ചരിത്രത്തിന്റെയും നിഗൂഢതകളുടെയും ലോകത്തേക്കുള്ള ഒരു യാത്രയാണ്.

ആദ്യം, ശാസ്ത്രത്തിന്റെ ലോകത്തേക്ക് കടക്കാം.
നമുക്ക് ചുറ്റുമുള്ള ലോകം എങ്ങനെ പ്രവർത്തിക്കുന്നു? പുതിയ കണ്ടുപിടിത്തങ്ങൾ നമ്മുടെ ജീവിതത്തെ എങ്ങനെ മാറ്റുന്നു? പ്രകൃതിയിലെ അത്ഭുതങ്ങൾക്ക് പിന്നിൽ എന്ത് ശാസ്ത്രമാണ് പ്രവർത്തിക്കുന്നത്?
ലളിതമായ വിശദീകരണങ്ങളിലൂടെയും രസകരമായ ദൃശ്യങ്ങളിലൂടെയും ശാസ്ത്രത്തെ കൂടുതൽ അടുത്തറിയാൻ ഇവിടെ നമുക്ക് ശ്രമിക്കാം.

അടുത്തതായി, ഭൂമിയുടെ അതിരുകൾക്കപ്പുറത്തേക്ക് നമുക്ക് യാത്ര ചെയ്യാം.
ഗ്രഹങ്ങൾ, നക്ഷത്രങ്ങൾ, ഗാലക്സികൾ, തമോഗർത്തങ്ങൾ, പ്രപഞ്ചത്തിന്റെ ഉത്ഭവത്തെക്കുറിച്ചുള്ള ശാസ്ത്രീയ കണ്ടെത്തലുകൾ…
നമ്മൾ ജീവിക്കുന്ന പ്രപഞ്ചത്തെക്കുറിച്ച് ശാസ്ത്രജ്ഞർ കണ്ടെത്തിയ കാര്യങ്ങളും ഇനിയും ഉത്തരം കണ്ടെത്തേണ്ട ചോദ്യങ്ങളും ഇവിടെ പരിചയപ്പെടാം.

ചരിത്രത്തിലും ഇന്നത്തെ ലോകത്തും നമ്മെ അത്ഭുതപ്പെടുത്തുന്ന നിരവധി സംഭവങ്ങളുണ്ട്.
പുരാതന നാഗരികതകൾ എങ്ങനെ വളർന്നു? ചരിത്രത്തിലെ ചില സംഭവങ്ങളെക്കുറിച്ച് ഇന്നും എന്തുകൊണ്ടാണ് ചർച്ചകൾ തുടരുന്നത്? നിഗൂഢമെന്ന് തോന്നുന്ന സംഭവങ്ങൾക്ക് പിന്നിൽ എന്തായിരിക്കാം?
തെളിവുകളെ അടിസ്ഥാനമാക്കി ഇത്തരം വിഷയങ്ങൾ പരിശോധിക്കാം. സ്ഥിരീകരിച്ച വസ്തുതകളെയും സിദ്ധാന്തങ്ങളെയും വെറും ഊഹങ്ങളെയും വേർതിരിച്ചറിയാനും ഇവിടെ ശ്രദ്ധിക്കാം.

നമ്മൾ എങ്ങനെ ചിന്തിക്കുന്നു? ചില കാര്യങ്ങളെ നമ്മൾ ഭയപ്പെടുന്നത് എന്തുകൊണ്ടാണ്? ഓർമ്മകൾ എങ്ങനെ രൂപപ്പെടുന്നു? നമ്മുടെ തീരുമാനങ്ങളെ സ്വാധീനിക്കുന്ന ഘടകങ്ങൾ എന്തൊക്കെയാണ്?
മനുഷ്യന്റെ മനസ്സിനെയും പെരുമാറ്റത്തെയും കുറിച്ചുള്ള മനഃശാസ്ത്രപരമായ അറിവുകളും രസകരമായ കണ്ടെത്തലുകളും നമുക്ക് പരിചയപ്പെടാം.

ഇതിനുപുറമേ, ലോകത്തെക്കുറിച്ചുള്ള അതിശയകരമായ വസ്തുതകൾ, പൊതുവിജ്ഞാനം, സാങ്കേതികവിദ്യ, പുതിയ കണ്ടെത്തലുകൾ, നമ്മൾ സാധാരണയായി ശ്രദ്ധിക്കാത്ത കാര്യങ്ങൾ എന്നിവയും ഈ ചാനലിൽ ഉണ്ടാകും.
ചില വിഷയങ്ങൾ നിങ്ങളെ അത്ഭുതപ്പെടുത്തും. ചിലത് കൂടുതൽ അന്വേഷിക്കാൻ പ്രേരിപ്പിക്കും. മറ്റുചിലത് നിങ്ങൾ ഇതുവരെ കരുതിയിരുന്ന കാര്യങ്ങളെ വീണ്ടും പരിശോധിക്കാൻ സഹായിക്കും.

കൂട്ടുകാരേ, മിസ്റ്ററി വേഴ്സ് മലയാളത്തിന്റെ ലക്ഷ്യം വിവരങ്ങൾ പറഞ്ഞുതരുക മാത്രമല്ല. പുതിയ കാര്യങ്ങൾ അറിയാനും ചോദ്യങ്ങൾ ചോദിക്കാനും തെളിവുകളുടെ അടിസ്ഥാനത്തിൽ ചിന്തിക്കാനും നിങ്ങളെ പ്രോത്സാഹിപ്പിക്കുക കൂടിയാണ്.
ഇവിടെ നമ്മൾ അറിയാത്ത കാര്യങ്ങൾ അന്വേഷിക്കും, പുതിയ കണ്ടെത്തലുകൾ പരിചയപ്പെടും, ഓരോ വിഷയത്തെയും കൗതുകത്തോടെ സമീപിക്കും.
ഈ യാത്രയിൽ നിങ്ങളും ഞങ്ങളോടൊപ്പം ചേരുമല്ലോ?
ചാനൽ സബ്സ്ക്രൈബ് ചെയ്യൂ. വീഡിയോ ഇഷ്ടപ്പെട്ടാൽ ലൈക്ക് ചെയ്യൂ. നിങ്ങൾക്ക് അറിയേണ്ട വിഷയങ്ങൾ കമന്റിലൂടെ നിർദേശിക്കൂ.
അപ്പോൾ, അറിവിന്റെ പുതിയൊരു യാത്രയ്ക്ക് നമുക്ക് തുടക്കം കുറിക്കാം.
ഇത് മിസ്റ്ററി വേഴ്സ് മലയാളം.
ചോദ്യങ്ങൾ ചോദിക്കൂ. അറിവ് തേടൂ. ലോകത്തെ പുതുതായി അറിയൂ!"""


async def synthesize_speech(text: str, voice: str, rate: str, pitch: str, raw_out: str):
    comm = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
    await comm.save(raw_out)
    print(f"Synthesized: {raw_out}")


def get_audio_duration(audio_file: str) -> float:
    cmd = [FFMPEG, "-i", audio_file, "-f", "null", "-"]
    res = subprocess.run(cmd, stderr=subprocess.PIPE, text=True)
    dur = 50.0
    for line in res.stderr.splitlines():
        if "Duration:" in line:
            parts = line.split("Duration:")[1].split(",")[0].strip().split(":")
            dur = float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
            break
    return dur


def mix_with_ambient_music(voice_mp3: str, out_mixed_mp3: str, total_pad_sec: float = 2.0):
    dur = get_audio_duration(voice_mp3)
    total_dur = dur + total_pad_sec
    filter_complex = (
        f"aevalsrc='0.025*sin(2*PI*108*t) + 0.015*sin(2*PI*216*t) + 0.010*sin(2*PI*432*t) + 0.005*sin(2*PI*648*t)':s=48000:d={total_dur}[music]; "
        f"[music]afade=t=in:ss=0:d=1.5,afade=t=out:st={total_dur - 2.0}:d=2.0[music_faded]; "
        f"[0:a]volume=1.0,apad=pad_dur={total_pad_sec}[voice]; "
        f"[voice][music_faded]amix=inputs=2:duration=longest:weights=1.0 0.25[aout]"
    )
    cmd = [
        FFMPEG, "-y",
        "-i", voice_mp3,
        "-filter_complex", filter_complex,
        "-map", "[aout]",
        "-c:a", "libmp3lame",
        "-b:a", "192k",
        "-ar", "48000",
        out_mixed_mp3
    ]
    subprocess.run(cmd, check=True)
    print(f"Mixed professional audio to {out_mixed_mp3} (duration: {total_dur:.2f}s)")
    return total_dur


def format_srt_time(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int(round((seconds - int(seconds)) * 1000))
    if ms >= 1000:
        ms = 999
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def build_srt_from_cues(cues: list) -> str:
    """cues format: [(start_sec, end_sec, text), ...]"""
    lines = []
    for idx, (s, e, text) in enumerate(cues, 1):
        lines.append(f"{idx}")
        lines.append(f"{format_srt_time(s)} --> {format_srt_time(e)}")
        lines.append(text)
        lines.append("")
    return "\n".join(lines)


def main():
    print("=" * 70)
    print("SYNTHESIZING APPROVED MALAYALAM NARRATION & TIMED ENGLISH SUBTITLES")
    print("=" * 70)

    # 1. SYNTHESIZE SHORT AUDIO
    raw_short = str(AUDIO_DIR / "raw_short_voice.mp3")
    final_short = str(AUDIO_DIR / "intro_short_kid.mp3")
    asyncio.run(synthesize_speech(SHORT_SCRIPT_MAL, "ml-IN-SobhanaNeural", "+2%", "+18Hz", raw_short))
    dur_short = mix_with_ambient_music(raw_short, final_short, total_pad_sec=2.0)
    print(f"Short Audio Total Duration: {dur_short:.2f}s")

    # Time cues proportionally for Short based on measured duration
    # 10 cues matching the 10 Malayalam sentences
    short_en_texts = [
        "Hello friends!",
        "There are so many things in this world that we don't yet know.",
        "The wonders of space, mysteries of history, marvels of science, secrets of the human mind...",
        "Are you curious to discover all of this?",
        "Then welcome... to MysteryVerse Malayalam!",
        "Here we will explore space, science, fascinating facts, and history.",
        "We will investigate mysteries and understand human thoughts and behavior.",
        "Every video will be an exciting journey into new knowledge.",
        "So join us on this journey. Subscribe to the channel, and comment your thoughts below.",
        "Together, let us uncover new discoveries!"
    ]
    # Proportional sentence weights based on Malayalam word counts
    short_weights = [1.5, 3.8, 6.2, 2.5, 3.8, 5.5, 6.5, 3.8, 6.5, 2.8]
    total_w = sum(short_weights)
    speech_dur = dur_short - 2.0
    start_t = 0.5
    short_cues = []
    for txt, w in zip(short_en_texts, short_weights):
        span = (w / total_w) * (speech_dur - 0.5)
        end_t = start_t + span
        short_cues.append((start_t, end_t, txt))
        start_t = end_t + 0.1

    srt_short_content = build_srt_from_cues(short_cues)
    for p in [SUB_DIR / "intro_short_en_clean.srt", SUB_DIR / "intro_short_en.srt"]:
        with open(p, "w", encoding="utf-8") as f:
            f.write(srt_short_content)
        print(f"Saved: {p}")

    # 2. SYNTHESIZE LONG AUDIO
    raw_long = str(AUDIO_DIR / "raw_long_voice.mp3")
    final_long = str(AUDIO_DIR / "intro_long_kid.mp3")
    asyncio.run(synthesize_speech(LONG_SCRIPT_MAL, "ml-IN-SobhanaNeural", "+2%", "+18Hz", raw_long))
    dur_long = mix_with_ambient_music(raw_long, final_long, total_pad_sec=3.0)
    print(f"Long Audio Total Duration: {dur_long:.2f}s")

    # Time cues proportionally for Long based on measured duration
    # 27 cues matching each sentence
    long_en_texts = [
        "Hello friends!",
        "Have you ever looked up at the night sky and wondered?",
        "In this vast universe, how many wonders remain unknown to us?",
        "Could there be undiscovered secrets in events that happened thousands of years ago?",
        "And how does our own human mind truly work?",
        "If questions like these make you think, you have come to the right place.",
        "Welcome... to MysteryVerse Malayalam!",
        "This is a journey into the world of knowledge, science, history, and mysteries.",
        "First, let us step into the realm of science.",
        "How does the world around us work, and how do new discoveries transform our lives?",
        "Through simple explanations and engaging visuals, we will explore the science behind nature's marvels.",
        "Next, let us journey beyond the boundaries of Earth.",
        "Planets, stars, galaxies, black holes, and scientific discoveries about the origin of the cosmos...",
        "We will explore what scientists have discovered about our universe, and the questions that remain.",
        "Throughout history and in the modern world, there are many events that astonish us.",
        "How did ancient civilizations rise? What really lies behind mysterious historical enigmas?",
        "We will examine these questions through evidence, separating verified facts and theories from mere speculation.",
        "How do we think? Why do we fear certain things?",
        "How are memories formed, and what influences our decisions?",
        "We will explore psychological insights and fascinating discoveries about the human mind and behavior.",
        "In addition, this channel will feature mind-blowing facts, general knowledge, technology, and hidden curiosities.",
        "Some topics will amaze you, others will inspire you to investigate, and some will prompt you to rethink what you knew.",
        "Friends, our goal is not just sharing facts, but encouraging you to ask questions and think critically.",
        "Here we will explore the unknown, discover new horizons, and approach every topic with curiosity.",
        "Will you join us on this extraordinary expedition?",
        "Subscribe to the channel, hit like, and suggest the topics you want to explore in the comments.",
        "Let us begin this new journey of discovery together. This is MysteryVerse Malayalam."
    ]
    long_weights = [
        1.5, 3.2, 4.0, 4.5, 3.0, 4.2, 3.5, 4.8, # Opening (~28.7s)
        2.5, 5.0, 6.0,                          # Science (~13.5s)
        3.0, 6.5, 6.0,                          # Space (~15.5s)
        3.5, 6.0, 7.5,                          # History & Mysteries (~17.0s)
        3.5, 4.0, 6.5,                          # Psychology (~14.0s)
        7.0, 6.5,                               # Amazing Facts (~13.5s)
        6.5, 6.0, 2.5, 5.5, 4.0                 # Closing (~24.5s)
    ]
    total_lw = sum(long_weights)
    speech_ldur = dur_long - 3.0
    start_lt = 0.5
    long_cues = []
    for txt, w in zip(long_en_texts, long_weights):
        span = (w / total_lw) * (speech_ldur - 0.5)
        end_lt = start_lt + span
        long_cues.append((start_lt, end_lt, txt))
        start_lt = end_lt + 0.1

    srt_long_content = build_srt_from_cues(long_cues)
    for p in [SUB_DIR / "intro_long_en_clean.srt", SUB_DIR / "intro_long_en.srt"]:
        with open(p, "w", encoding="utf-8") as f:
            f.write(srt_long_content)
        print(f"Saved: {p}")

    print("\nAUDIO & SUBTITLE GENERATION COMPLETE!")


if __name__ == "__main__":
    main()
