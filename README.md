# MYSTERYVERSE AI — Autonomous YouTube Media Command Suite

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Channel: MYSTERY VERSE MALAYALAM](https://img.shields.io/badge/YouTube-%40MYSTERYVERSE--MALAYALAM-red)](https://www.youtube.com/@MYSTERYVERSE-MALAYALAM)
[![Target: 60 Videos/Month](https://img.shields.io/badge/Monthly%20Target-60%20Videos%20(30%20Shorts%20%2B%2030%20Longs)-cyan)](#)
[![Budget: ₹0](https://img.shields.io/badge/Recurring%20Cost-%E2%82%B90%20Zero%20Budget-emerald)](#)

**MYSTERYVERSE AI** is an autonomous, production-oriented media system designed to operate the Malayalam YouTube channel **[MYSTERY VERSE MALAYALAM (@MYSTERYVERSE-MALAYALAM)](https://www.youtube.com/@MYSTERYVERSE-MALAYALAM)**.

The system features the official 3D host **`jobelessboy`** (ജോബ്‌ലെസ്സ് ബോയ്) — a curious, expressive Pixar-style young explorer who guides viewers through cosmic mysteries, ancient civilisations, deep-sea exploration, and scientific breakthroughs.

- **Vercel Cloud Ready**: Instant deployment with root `vercel.json` and Vite SPA routing.
- **Autonomous Research & Fact Checking**: Multi-source RSS, arXiv, Wikipedia, NASA, Nature.
- **Authentic Malayalam Voice Narration**: Energetic kid voice via Edge-TTS (`ml-IN-MidhunNeural` with tuned pitch & rate).
- **High-Impact English Subtitles**: Clean, burn-in typography ensuring zero broken Indic font conjuncts on mobile devices.
- **Character Studio**: 6 canonical 3D expressions for `jobelessboy` (Explanation, Surprise, Curiosity, Excitement, Caution, Humour).
- **Procedural 3D & FFmpeg Pipeline**: 1080x1920 YouTube Shorts and 1920x1080 Widescreen intros with dynamic space and earth fly-in animation.
- **YouTube Data API v3 Scheduler**: Pre-configured for IST publishing hours (18:30 IST Shorts, 20:00 IST Longs) and YPP Monetisation tracking.

---

## Deploy to Vercel

1. Push this repository to `https://github.com/AjinLabs/mysteryverse-ai`.
2. Go to [Vercel](https://vercel.com) and click **"Add New" > "Project"**.
3. Import **`AjinLabs/mysteryverse-ai`**.
4. Leave settings as default (root `vercel.json` automatically configures Vite build output to `frontend/dist`).
5. Click **Deploy**. Your live dashboard will be instantly active with built-in telemetry, video vault previews, and character studio.

## Architecture Overview

```
MYSTERYVERSE AI
├── backend/
│   ├── app/
│   │   ├── main.py                     # FastAPI application & static mount
│   │   ├── config.py                   # System paths, targets, zero-budget policy
│   │   ├── database.py                 # SQLite engine & system log auditor
│   │   ├── scheduler.py                # Autonomous workflow state machine
│   │   ├── agents/
│   │   │   ├── research_agent.py       # Topic discovery across 9 pillars
│   │   │   ├── script_agent.py         # Malayalam narration generator
│   │   │   ├── fact_checker.py         # Fact verification & conspiracy detection
│   │   │   └── deduplicator.py         # Title & n-gram uniqueness checker
│   │   ├── character/
│   │   │   ├── bible.py                # Character bible for Dr. Kiran
│   │   │   └── assets_manager.py       # Procedural sprite generator (6 expressions)
│   │   ├── animation/
│   │   │   ├── blender_pipeline.py     # Blender CLI automation
│   │   │   └── procedural_engine.py    # Ultra-fast PIL + FFmpeg 3D scene renderer
│   │   ├── audio/
│   │   │   ├── tts_service.py          # Edge-TTS Malayalam voice engine
│   │   │   ├── subtitle_service.py     # Synchronized SRT/WebVTT generator
│   │   │   └── music_effects.py        # Procedural synth ambient drone generator
│   │   ├── video/
│   │   │   └── ffmpeg_compositor.py    # FFmpeg video assembler & validator
│   │   ├── thumbnail/
│   │   │   └── thumbnail_engine.py     # High-CTR Malayalam thumbnail engine
│   │   ├── youtube/
│   │   │   ├── oauth_manager.py        # Official Google OAuth 2.0 flow
│   │   │   ├── uploader.py             # YouTube Data API v3 scheduler
│   │   │   ├── channel_audit.py        # Channel settings & manual action audit
│   │   │   └── analytics.py            # YPP Monetisation calculator
│   │   ├── quality/
│   │   │   └── gatekeeper.py           # Multi-factor quality & policy gates
│   │   └── api/                        # REST API endpoints
│   ├── data/                           # SQLite database & OAuth tokens
│   └── static/                         # Generated videos, audio, thumbnails, sprites
├── frontend/                           # React 19 + TypeScript + Vite HUD Command Suite
├── scripts/                            # Blender headless render script
├── tests/                              # Pytest automated test suite
└── docs/                               # Setup & operation documentation
```

---

## Quickstart

### 1. Launch Backend:
```powershell
cd c:\m\backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

### 2. Launch Frontend:
```powershell
cd c:\m\frontend
npm.cmd run dev
```

Open `http://localhost:5173` to access the Command Center.

---

## Verification & Test Results

All 6 automated unit and integration tests passed:
- `test_research_discovery_and_deduplication` [PASSED]
- `test_fact_checker_audit` [PASSED]
- `test_malayalam_script_generation` [PASSED]
- `test_subtitle_timing_generator` [PASSED]
- `test_ffmpeg_compositor_validation` [PASSED]
- `test_youtube_scheduling_kolkata_timezone` [PASSED]

End-to-end production verification produced:
- Video: `job_cfb9277c95_final.mp4` (1.5 MB, 1080x1920 HD, H.264 + AAC, valid streams)
- Audio: `job_cfb9277c95_voice.mp3` (Malayalam Neural TTS via `ml-IN-MidhunNeural`)
- Subtitles: `job_cfb9277c95_sub.srt` (Accurately timed Malayalam captions)
- Thumbnail: `job_cfb9277c95_thumb.jpg` (1280x720, bold Nirmala UI Malayalam typography + Dr. Kiran cutout)
- Quality Gate: **PASSED ALL GATES**
- YouTube Upload: Scheduled for `2026-10-26T18:30:00+05:30` (Asia/Kolkata).
