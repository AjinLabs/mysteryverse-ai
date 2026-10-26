# MYSTERYVERSE AI — PRODUCTION SETUP & OPERATION MANUAL
**Channel Target:** [MYSTERY VERSE MALAYALAM (@MYSTERYVERSE-MALAYALAM)](https://www.youtube.com/@MYSTERYVERSE-MALAYALAM)  
**Language:** Malayalam (മലയാളം)  
**Budget Target:** ₹0 Recurring Expenditure (100% Free-Tier & Local Assembly)

---

## 1. System Requirements & Toolchains

| Dependency | Required Version | Status on System | Notes |
| :--- | :--- | :--- | :--- |
| **Operating System** | Windows 10/11 64-bit | Verified | PowerShell 5.1+ / 7+ |
| **Python** | 3.10 – 3.14 | Installed (3.14.8) | FastAPI, SQLite, PIL, Edge-TTS |
| **Node.js & npm** | Node v18+, npm v9+ | Installed (Node 24, npm 11) | React 19 + TypeScript + Vite |
| **FFmpeg** | 6.0+ | **v7.1 Essentials Embedded** | Embedded via `imageio-ffmpeg` / Windows PATH |
| **Blender** | 3.6+ / 4.x | Auto-Detected | Procedural motion graphics engine handles 100% of renders even without Blender! |
| **Malayalam Fonts** | Indic font with Malayalam | `C:\Windows\Fonts\Nirmala.ttc` | Native Microsoft font for crisp thumbnail & subtitle typography |

---

## 2. Quickstart: Launching the Autonomous Suite

### Terminal 1: FastAPI Backend & Autonomous Scheduler
```powershell
cd c:\m\backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```
- API Base: `http://localhost:8000/api`
- Swagger Interactive Docs: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/api/health`

### Terminal 2: React HUD Command Center
```powershell
cd c:\m\frontend
npm.cmd run dev
```
- Web Dashboard: `http://localhost:5173`

---

## 3. Account Security & Google OAuth 2.0 Setup

The owner must **never** paste their Gmail password or YouTube login into code or config files. MYSTERYVERSE AI uses the official Google OAuth 2.0 authorization code flow.

### Step-by-Step Google Cloud Console Walkthrough:
1. Open [Google Cloud Console](https://console.cloud.google.com/).
2. Create or select a project named `Mysteryverse-Media`.
3. In the sidebar, navigate to **APIs & Services** > **Library**, search for **YouTube Data API v3**, and click **Enable**.
4. Navigate to **APIs & Services** > **OAuth Consent Screen**:
   - User Type: **External**
   - App Name: `MYSTERYVERSE AI Autonomous Suite`
   - Scopes:
     - `https://www.googleapis.com/auth/youtube.upload`
     - `https://www.googleapis.com/auth/youtube.readonly`
     - `https://www.googleapis.com/auth/youtube.force-ssl`
5. Navigate to **APIs & Services** > **Credentials**:
   - Click **Create Credentials** > **OAuth Client ID**.
   - Application Type: **Web Application**
   - Authorized redirect URIs:
     ```
     http://localhost:8000/api/youtube/oauth2callback
     ```
6. Click **Download JSON**, rename the file to `client_secrets.json`, and place it in:
   ```
   c:\m\backend\data\client_secrets.json
   ```
7. Open the dashboard at `http://localhost:5173`, navigate to the **YouTube & Audit** tab, and click **Connect Channel**.
8. Sign in with the Google Account owning **MYSTERY VERSE MALAYALAM (@MYSTERYVERSE-MALAYALAM)** and authorize.
9. Tokens are automatically and securely stored in `c:\m\backend\data\oauth_token.json` (gitignored).

---

## 4. YouTube Channel Settings & Studio Actions

Certain critical settings are protected by YouTube and **cannot** be modified via third-party APIs:

1. **Google AdSense Account Association:**
   - Go to [YouTube Studio](https://studio.youtube.com/) > **Earn Tab** > Link your approved AdSense account. (Never share banking passwords).
2. **2-Step Verification:**
   - Go to [Google Security](https://myaccount.google.com/security) and activate 2-Step Verification.
3. **Advanced Features Phone Verification:**
   - Go to YouTube Studio > Settings > Channel > Feature Eligibility > Verify Phone Number (enables daily uploads > 10 videos).

---

## 5. Publishing Cadence & Asia/Kolkata Scheduling

The automated scheduler calculates prime release slots in `Asia/Kolkata` (IST) timezone:
- **YouTube Shorts (1080x1920):** 18:30 IST (Prime mobile browsing hours in Kerala)
- **Long-Form Videos (1920x1080):** 20:00 IST (Prime evening educational viewing)

All videos are initially uploaded as **Private** with a `publishAt` parameter, allowing the owner to preview the release or let YouTube publish automatically at the scheduled hour.

---

## 6. Emergency Kill Switch & Safety Controls

To instantly halt all rendering, scheduling, and YouTube uploads:
- Click the red **KILL SWITCH** button in the dashboard top navigation bar, OR
- Create the lockfile manually:
  ```powershell
  New-Item c:\m\backend\data\KILLSWITCH_ACTIVE
  ```
The system will immediately pause all background jobs and prevent any outbound YouTube requests until cleared.
