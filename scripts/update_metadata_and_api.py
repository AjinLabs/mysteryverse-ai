def refine_backend_api():
    path = "api/index.py"
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    text = text.replace(
        '"topic_title": "MysteryVerse Channel Introduction Short"',
        '"topic_title": "What If the Sun Suddenly Disappeared?"'
    )
    text = text.replace(
        '"topic_title": "MysteryVerse Full Channel Introduction"',
        '"topic_title": "What If the Sun Disappeared? Complete Scientific Breakdown"'
    )
    text = text.replace(
        '"malayalam_narration": "നമസ്കാരം കൂട്ടുകാരേ! MysteryVerse-ലേക്ക് എല്ലാവർക്കും സ്വാഗതം! ഈ ലോകം നിറയെ നമ്മളെ അത്ഭുതപ്പെടുത്തുന്ന കാര്യങ്ങളുണ്ട്...",',
        '"malayalam_narration": "Imagine waking up one morning and looking outside your window. The sky is completely dark. The sunlight is gone...",'
    )
    text = text.replace(
        '"english_translation": "Hey friends! Welcome to MysteryVerse! This world is full of things that amaze us...",',
        '"english_translation": "Imagine waking up one morning and looking outside your window. The sky is completely dark. The sunlight is gone...",'
    )
    text = text.replace(
        '"instruction": "Set Video language to Malayalam and Captions to \'None\' or English captions provided by system."',
        '"instruction": "Set Video language to English and Captions to English captions provided by system."'
    )

    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    print("api/index.py refined successfully.")

if __name__ == "__main__":
    refine_backend_api()

def update_backend_config():
    path = "backend/app/config.py"
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    text = text.replace('TARGET_CHANNEL_NAME = "MYSTERY VERSE MALAYALAM"', 'TARGET_CHANNEL_NAME = "MysteryVerse"')
    text = text.replace('TARGET_CHANNEL_HANDLE = "@MYSTERYVERSE-MALAYALAM"', 'TARGET_CHANNEL_HANDLE = "@MysteryVerse"')
    text = text.replace('TARGET_CHANNEL_URL = "https://www.youtube.com/@MYSTERYVERSE-MALAYALAM"', 'TARGET_CHANNEL_URL = "https://www.youtube.com/@MysteryVerse"')
    text = text.replace('DEFAULT_MALE_VOICE = "ml-IN-MidhunNeural"', 'DEFAULT_MALE_VOICE = "en-US-AndrewNeural"')
    text = text.replace('DEFAULT_FEMALE_VOICE = "ml-IN-SobhanaNeural"', 'DEFAULT_FEMALE_VOICE = "en-US-AvaNeural"')

    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    print("backend/app/config.py updated")

if __name__ == "__main__":
    update_backend_config()

def update_bible():
    path = "backend/app/character/bible.py"
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    text = text.replace('"channel": "MYSTERY VERSE MALAYALAM (@MYSTERYVERSE-MALAYALAM)",', '"channel": "MysteryVerse (@MysteryVerse)",')
    text = text.replace('"language": "Conversational, modern articulate Malayalam (മലയാളം)",', '"language": "Conversational, articulate, globally engaging English",')
    text = text.replace('"tagline": "ജോലിയില്ലെങ്കിലും പ്രപഞ്ച രഹസ്യങ്ങൾ മുഴുവൻ ഞാൻ ചുരുളഴിച്ചിരിക്കും! (Uncovering the universe, one mystery at a time)"', '"tagline": "Unlocking the Universe\'s Greatest Scientific Mysteries, one revelation at a time!"')

    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    print("backend/app/character/bible.py updated")

def update_gatekeeper():
    path = "backend/app/quality/gatekeeper.py"
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    # Allow English scripts as well
    old_block = """        # 3. Malayalam Script & Language Integrity
        full_script = script.get("full_script_mal", "")
        # Verify Malayalam Unicode block (\\u0D00-\\u0D7F)
        malayalam_chars = [c for c in full_script if '\\u0D00' <= c <= '\\u0D7F']
        has_malayalam = len(malayalam_chars) > 20
        checks["language_integrity"] = {
            "language": "Malayalam",
            "malayalam_char_count": len(malayalam_chars),
            "passed": has_malayalam
        }
        if not has_malayalam:
            critical_failures.append("Script does not contain sufficient verified Malayalam text")"""

    new_block = """        # 3. Script & Language Integrity (English & Global Audience)
        full_script = script.get("full_script_en", "") or script.get("full_script_mal", "") or script.get("narration", "")
        has_script = len(full_script.strip().split()) >= 10
        checks["language_integrity"] = {
            "language": "English",
            "word_count": len(full_script.strip().split()),
            "passed": has_script
        }
        if not has_script:
            critical_failures.append("Script does not contain sufficient verified narration text")"""

    text = text.replace(old_block, new_block)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    print("backend/app/quality/gatekeeper.py updated")

if __name__ == "__main__":
    update_bible()
    update_gatekeeper()
