import asyncio
import os
import subprocess
import edge_tts
import imageio_ffmpeg

ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()

VOICE = "en-US-AndrewNeural"

SHORT_PARAGRAPHS = [
    "Hello, friends!",
    "There are so many things in this world that we still don't know. The wonders of space, the mysteries of history, the marvels of science, the secrets of the human mind.",
    "Would you like to find out about all of this?",
    "Then welcome to MysteryVerse!",
    "Here we will learn about space, science, interesting facts and history.",
    "We will investigate mysterious events. We will try to understand human thoughts and behaviour. We will look for answers to questions we don't usually ask.",
    "Every video will be a journey to something new.",
    "So join us on this journey of discovery. Subscribe to the channel. Tell us in the comments what you want to learn next.",
    "Let's discover new things together!"
]

LONG_PARAGRAPHS = [
    "Hello, friends!",
    "Have you ever looked up at the night sky and wondered? In this vast universe, how many things must there be that we don't know? Could events from thousands of years ago still hold secrets nobody has found? And how does our own mind actually work?",
    "If questions like these make you think too, you've come to the right place.",
    "Welcome to MysteryVerse!",
    "This is a journey into the world of knowledge, science, history and mysteries.",
    "First, let's step into the world of science.",
    "How does the world around us work? How do new inventions change our lives? What science is at work behind the wonders of nature?",
    "With simple explanations and fascinating visuals, let's try to understand science more closely.",
    "Next, let's travel beyond the edges of the Earth.",
    "Planets, stars, galaxies, black holes, and the scientific discoveries about the origin of the universe.",
    "Here we'll look at what scientists have found about the universe we live in, and the questions that still have no answers.",
    "There are many events, in history and in today's world, that amaze us.",
    "How did ancient civilizations grow? Why are some events in history still debated today? What could be behind events that seem mysterious?",
    "Let's examine such topics based on evidence. We'll also take care to tell confirmed facts, theories and plain guesses apart.",
    "How do we think? Why are we afraid of certain things? How are memories formed? What factors influence our decisions?",
    "Let's explore what psychology has learned about the human mind and behaviour, and some interesting discoveries.",
    "Besides this, the channel will also bring amazing facts about the world, general knowledge, technology, new discoveries, and things we usually don't notice.",
    "Some topics will amaze you. Some will make you want to dig deeper. Others will help you take a fresh look at what you thought you knew.",
    "Friends, the aim of MysteryVerse is not just to tell you facts. It is also to encourage you to learn new things, ask questions, and think based on evidence.",
    "Here we will investigate what we don't know, get to know new discoveries, and approach every subject with curiosity.",
    "Will you join us on this journey?",
    "Subscribe to the channel. If you like the video, give it a like. Suggest the topics you want to learn about in the comments.",
    "So let's begin a new journey of discovery.",
    "This is MysteryVerse.",
    "Ask questions. Seek knowledge. See the world anew!"
]

async def generate_speech_with_subs(paragraphs, base_name, out_dir_audio, out_dir_subs):
    os.makedirs(out_dir_audio, exist_ok=True)
    os.makedirs(out_dir_subs, exist_ok=True)
    
    mp3_path = os.path.join(out_dir_audio, f"{base_name}.mp3")
    wav_path = os.path.join(out_dir_audio, f"{base_name}.wav")
    srt_path = os.path.join(out_dir_subs, f"{base_name}.srt")
    
    # We join with double newline or pause
    # To get clean timing and nice pacing, we can synthesize each paragraph or the whole text
    # Synthesizing paragraph by paragraph with a short silence yields perfect per-paragraph subtitles!
    
    submaker = edge_tts.SubMaker()
    total_audio_bytes = bytearray()
    
    # Let's concatenate text with clear paragraph spacing
    full_text = "\n\n".join(paragraphs)
    
    comm = edge_tts.Communicate(full_text, VOICE, rate="+3%", pitch="+4Hz")
    
    with open(mp3_path, "wb") as f:
        async for chunk in comm.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] in ("SentenceBoundary", "WordBoundary"):
                submaker.feed(chunk)
                
    with open(srt_path, "w", encoding="utf-8") as f:
        f.write(submaker.get_srt())
        
    # Convert MP3 to 24kHz Mono WAV and apply gentle broadcast loudness normalization (-14 LUFS)
    # Using ffmpeg loudnorm filter
    cmd = [
        ffmpeg_bin, "-i", mp3_path,
        "-af", "loudnorm=I=-14:LRA=11:TP=-1.5",
        "-ar", "24000", "-ac", "1",
        wav_path, "-y"
    ]
    subprocess.run(cmd, check=True)
    print(f"Generated {wav_path} and {srt_path}")

async def main():
    print("Synthesizing Short...")
    await generate_speech_with_subs(SHORT_PARAGRAPHS, "intro_short_en", "c:/m/output/audio", "c:/m/output/subtitles")
    print("Synthesizing Long...")
    await generate_speech_with_subs(LONG_PARAGRAPHS, "intro_long_en", "c:/m/output/audio", "c:/m/output/subtitles")
    print("Done!")

if __name__ == "__main__":
    asyncio.run(main())

