import asyncio
import os
import subprocess
import edge_tts
import imageio_ffmpeg
from datetime import timedelta
import re
import numpy as np
import scipy.io.wavfile as wav

ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
VOICE = "en-US-AndrewNeural"

OUT_AUDIO = r"c:\m\output\audio"
OUT_SUBS = r"c:\m\output\subtitles"
os.makedirs(OUT_AUDIO, exist_ok=True)
os.makedirs(OUT_SUBS, exist_ok=True)

SHORT_SCRIPT = (
    "Imagine waking up one morning, looking outside your window, and the sky is pitch black. "
    "The Sun has completely disappeared! "
    "What would happen to Earth? Would we freeze instantly? "
    "Surprisingly, no. For the first eight minutes and twenty seconds, we wouldn't even notice. "
    "Sunlight takes that long to travel ninety-three million miles to reach Earth. "
    "For eight minutes, the world would carry on completely normally. "
    "Then, utter darkness. "
    "Within days, global temperatures plummet. "
    "Within weeks, the oceans begin to freeze from the surface down. "
    "Could humanity survive without our star? "
    "Only by moving deep underground, powered by geothermal and nuclear energy. "
    "Subscribe to MysteryVerse for more mind-blowing science mysteries! "
    "Stay curious!"
)

LONG_SECTIONS = [
    # 1. The Impossible Morning
    "Imagine waking up one morning and looking outside your window. "
    "The sky is completely dark. The sunlight is gone. Stars are visible even though it should be daytime. "
    "The Sun, the star that gives Earth light and warmth, has suddenly disappeared. "
    "What would happen to our planet? Would we freeze instantly? Would the oceans turn into ice? And could humanity survive? "
    "Today, on MysteryVerse, we're exploring one of the most fascinating thought experiments in science. "
    "What would really happen if the Sun suddenly disappeared?",

    # 2. The Eight-Minute Mystery
    "Here's the first surprising fact. "
    "If the Sun disappeared, we wouldn't see the change immediately. "
    "Why? "
    "Because sunlight takes approximately eight minutes and twenty seconds to travel from the Sun to Earth. "
    "That means the sunlight reaching our planet right now left the Sun more than eight minutes ago. "
    "In this hypothetical situation, Earth would continue receiving sunlight for a little over eight minutes after the Sun disappeared. "
    "For that brief period, our world would look completely normal. "
    "People would continue working. Cars would travel along roads. Birds would fly through the sky. "
    "Then, the light would stop arriving. "
    "The daytime sky would become dark, and the stars would become visible. "
    "It would be one of the strangest moments imaginable.",

    # 3. Would Earth Freeze Instantly?
    "Now comes the next question. "
    "Would the entire planet freeze in a matter of seconds? "
    "No. Earth would begin losing heat, but its temperature wouldn't suddenly drop everywhere. "
    "Our planet stores enormous amounts of thermal energy in its oceans, atmosphere, and land. "
    "Without sunlight, Earth's surface would gradually cool. "
    "The rate of cooling would vary depending on location, weather, geography, and ocean conditions. "
    "Over time, temperatures would fall, making many regions increasingly difficult to inhabit. "
    "The world wouldn't become a frozen ball instantly. The changes would unfold over time.",

    # 4. What Would Happen to Plants and Animals?
    "The Sun is more than a source of light. "
    "It powers almost all major food chains on Earth. "
    "Plants use sunlight for photosynthesis, the process that converts light energy into chemical energy. "
    "Without sunlight, photosynthesis would largely stop. "
    "Plants would no longer be able to produce new energy-rich material in the usual way. "
    "As plant growth declined, animals that depended on plants would struggle to find food. "
    "Predators would then face declining prey populations. "
    "Agriculture would be devastated unless humans could rely on artificial growing systems and alternative energy sources. "
    "Food production would become one of humanity's biggest challenges. "
    "However, not every ecosystem depends directly on sunlight. Some deep-sea communities survive using chemical energy from Earth's interior. "
    "Even in a world without the Sun, certain unusual environments might continue supporting life for some time.",

    # 5. The Strange Truth About Earth's Orbit
    "Here's a detail that makes this thought experiment even more fascinating. "
    "The Sun's gravity keeps Earth moving along its orbit. "
    "If the Sun disappeared, would Earth immediately fly away? "
    "Not instantly. "
    "According to relativity, changes in the gravitational field propagate at the speed of light. "
    "So Earth would continue following approximately its usual orbit until the change in gravitational influence reached it, roughly eight minutes and twenty seconds later. "
    "After that, Earth's motion would change dramatically. "
    "Earth would continue moving through space along a path determined by its existing velocity and the gravitational forces that remained. "
    "The disappearance of the Sun would therefore affect not only our planet's light and temperature, but also its journey through space. "
    "Of course, this is a theoretical scenario, not a realistic prediction of something expected to happen.",

    # 6. Could Humanity Survive?
    "Could humans survive without the Sun? "
    "Long-term survival would be extraordinarily difficult. "
    "However, technology could potentially help some people survive for a time. "
    "Geothermal energy and nuclear power could provide heat and electricity. "
    "Artificial lighting could help grow plants indoors. "
    "Protected underground facilities might offer shelter from extreme surface conditions. "
    "But supporting billions of people, maintaining infrastructure, and producing enough food would be an enormous challenge. "
    "The Sun is fundamental to the conditions that make life on Earth possible. "
    "Without it, our planet would become a radically different place.",

    # 7. The Final Revelation
    "The next time you see a sunrise, remember what it represents. "
    "The Sun powers our climate, supports photosynthesis, and provides the energy that sustains Earth's ecosystems. "
    "A single star makes our familiar world possible. "
    "And that's what makes science so fascinating. Even an impossible thought experiment can help us understand how deeply connected everything is. "
    "Now here's a question for you. "
    "What would you like to explore next: black holes, alien life, or the mysteries of the human brain? "
    "Share your answer in the comments. "
    "Subscribe to MysteryVerse for more fascinating discoveries, mind-blowing facts, and mysteries of our universe. "
    "Stay curious. Keep discovering. And never stop asking questions."
]

def format_timestamp(seconds):
    td = timedelta(seconds=seconds)
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

def generate_ambient_bed(path=os.path.join(OUT_AUDIO, "cinematic_ambient_bed.wav")):
    sr = 24000
    duration = 150
    total_samples = sr * duration
    t = np.linspace(0, duration, total_samples, endpoint=False)
    
    drone1 = 0.35 * np.sin(2 * np.pi * 55.0 * t)
    drone2 = 0.20 * np.sin(2 * np.pi * 110.0 * t + 0.5)
    drone3 = 0.12 * np.sin(2 * np.pi * 164.81 * t + 1.0)
    sub = 0.30 * np.sin(2 * np.pi * 27.5 * t)
    shimmer = 0.05 * np.sin(2 * np.pi * 440.0 * t) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.2 * t))
    
    bed = drone1 + drone2 + drone3 + sub + shimmer
    bed = bed / np.max(np.abs(bed)) * 0.45
    
    fade_len = sr * 4
    fade_in = np.linspace(0, 1, fade_len)
    fade_out = np.linspace(1, 0, fade_len)
    bed[:fade_len] *= fade_in
    bed[-fade_len:] *= fade_out
    
    bed_i16 = (bed * 32767).astype(np.int16)
    wav.write(path, sr, bed_i16)
    print(f"Generated Cinematic Ambient Bed: {path}")

async def synthesize_short():
    print("Synthesizing Sun Short Voiceover...", flush=True)
    mp3_path = os.path.join(OUT_AUDIO, "sun_short_en.mp3")
    wav_path = os.path.join(OUT_AUDIO, "sun_short_en.wav")
    srt_path = os.path.join(OUT_SUBS, "sun_short_en.srt")
    
    comm = edge_tts.Communicate(SHORT_SCRIPT, VOICE, rate="+2%", pitch="+2Hz")
    submaker = edge_tts.SubMaker()
    
    with open(mp3_path, "wb") as f:
        async for chunk in comm.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] in ("SentenceBoundary", "WordBoundary"):
                submaker.feed(chunk)
                
    with open(srt_path, "w", encoding="utf-8") as f:
        f.write(submaker.get_srt())
        
    cmd = [
        ffmpeg_bin, "-i", mp3_path,
        "-af", "loudnorm=I=-14:LRA=11:TP=-1.5",
        "-ar", "24000", "-ac", "1",
        wav_path, "-y"
    ]
    subprocess.run(cmd, check=True)
    print(f"Generated Short Audio: {wav_path} and Subtitles: {srt_path}", flush=True)

async def synthesize_long():
    print("Synthesizing Sun Long 7 Sections Voiceover...", flush=True)
    temp_dir = os.path.join(OUT_AUDIO, "long_parts")
    os.makedirs(temp_dir, exist_ok=True)
    
    section_files = []
    all_cues = []
    current_time_offset = 0.0
    cue_counter = 1

    for idx, text in enumerate(LONG_SECTIONS):
        sec_num = idx + 1
        part_mp3 = os.path.join(temp_dir, f"part_{sec_num:02d}.mp3")
        part_wav = os.path.join(temp_dir, f"part_{sec_num:02d}.wav")
        print(f"Synthesizing Long Section {sec_num}/7...", flush=True)
        
        comm = edge_tts.Communicate(text, VOICE, rate="+0%", pitch="+2Hz")
        submaker = edge_tts.SubMaker()
        
        with open(part_mp3, "wb") as f:
            async for chunk in comm.stream():
                if chunk["type"] == "audio":
                    f.write(chunk["data"])
                elif chunk["type"] in ("SentenceBoundary", "WordBoundary"):
                    submaker.feed(chunk)
                    
        subprocess.run([ffmpeg_bin, "-i", part_mp3, "-ar", "24000", "-ac", "1", part_wav, "-y"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        probe = subprocess.run([ffmpeg_bin, "-i", part_wav], capture_output=True, text=True)
        dur = 0.0
        for l in probe.stderr.split('\n'):
            if "Duration:" in l:
                m = re.search(r'Duration:\s*(\d+):(\d+):(\d+\.\d+)', l)
                if m:
                    h, mins, s = m.groups()
                    dur = int(h)*3600 + int(mins)*60 + float(s)
                    break
        
        srt_raw = submaker.get_srt()
        blocks = re.split(r'\n\s*\n', srt_raw.strip())
        for block in blocks:
            lines = block.split('\n')
            if len(lines) >= 3:
                time_match = re.search(r'(\d+):(\d+):(\d+),(\d+)\s*-->\s*(\d+):(\d+):(\d+),(\d+)', lines[1])
                if time_match:
                    h1, m1, s1, ms1, h2, m2, s2, ms2 = map(int, time_match.groups())
                    st = h1 * 3600 + m1 * 60 + s1 + ms1 / 1000.0 + current_time_offset
                    et = h2 * 3600 + m2 * 60 + s2 + ms2 / 1000.0 + current_time_offset
                    content = ' '.join(lines[2:]).strip()
                    all_cues.append((cue_counter, st, et, content))
                    cue_counter += 1
                    
        section_files.append(part_wav)
        current_time_offset += (dur + 0.5)

    concat_list_file = os.path.join(temp_dir, "concat_list.txt")
    silence_wav = os.path.join(temp_dir, "silence_half_sec.wav")
    subprocess.run([ffmpeg_bin, "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono", "-t", "0.5", silence_wav, "-y"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    with open(concat_list_file, "w") as f:
        for i, sf in enumerate(section_files):
            f.write(f"file '{sf.replace(os.sep, '/')}'\n")
            if i < len(section_files) - 1:
                f.write(f"file '{silence_wav.replace(os.sep, '/')}'\n")

    combined_wav = os.path.join(OUT_AUDIO, "sun_long_en.wav")
    cmd_concat = [
        ffmpeg_bin, "-f", "concat", "-safe", "0", "-i", concat_list_file,
        "-af", "loudnorm=I=-14:LRA=11:TP=-1.5",
        "-ar", "24000", "-ac", "1",
        combined_wav, "-y"
    ]
    subprocess.run(cmd_concat, check=True)

    combined_srt = os.path.join(OUT_SUBS, "sun_long_en.srt")
    with open(combined_srt, "w", encoding="utf-8") as f:
        for c_idx, st, et, txt in all_cues:
            f.write(f"{c_idx}\n{format_timestamp(st)} --> {format_timestamp(et)}\n{txt}\n\n")

    print(f"Generated Long Video Audio: {combined_wav} (Duration: ~{current_time_offset:.1f}s, {len(all_cues)} cues)", flush=True)

async def main():
    generate_ambient_bed()
    await synthesize_short()
    await synthesize_long()
    print("All audio and subtitles synthesized successfully!")

if __name__ == "__main__":
    asyncio.run(main())
