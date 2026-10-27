import os
import glob
import sqlite3

KEEP_VIDEOS = {'mysteryverse_intro_short.mp4', 'mysteryverse_intro_long.mp4'}
KEEP_THUMBS = {'mysteryverse_intro_short_thumb.jpg', 'mysteryverse_intro_long_thumb.jpg'}
KEEP_SUBS = {'intro_short_en.srt', 'intro_long_en.srt'}
KEEP_AUDIO = {'intro_short_kid.mp3', 'intro_long_kid.mp3'}

# 1. Clean output/
for f in os.listdir('c:/m/output'):
    fp = os.path.join('c:/m/output', f)
    if os.path.isfile(fp):
        if f not in KEEP_VIDEOS and f not in KEEP_THUMBS:
            print('Removing from output:', f)
            try:
                os.remove(fp)
            except Exception as e:
                print('Error removing:', fp, e)

# 2. Clean backend static videos
for f in os.listdir('c:/m/backend/static/videos'):
    fp = os.path.join('c:/m/backend/static/videos', f)
    if os.path.isfile(fp) and f not in KEEP_VIDEOS:
        print('Removing from backend/static/videos:', f)
        try:
            os.remove(fp)
        except Exception as e:
            print('Error removing:', fp, e)

# 3. Clean frontend public static videos
for f in os.listdir('c:/m/frontend/public/static/videos'):
    fp = os.path.join('c:/m/frontend/public/static/videos', f)
    if os.path.isfile(fp) and f not in KEEP_VIDEOS:
        print('Removing from frontend/public/static/videos:', f)
        try:
            os.remove(fp)
        except Exception as e:
            print('Error removing:', fp, e)

# 4. Clean frontend dist static videos
if os.path.exists('c:/m/frontend/dist/static/videos'):
    for f in os.listdir('c:/m/frontend/dist/static/videos'):
        fp = os.path.join('c:/m/frontend/dist/static/videos', f)
        if os.path.isfile(fp) and f not in KEEP_VIDEOS:
            print('Removing from frontend/dist/static/videos:', f)
            try:
                os.remove(fp)
            except Exception as e:
                print('Error removing:', fp, e)

# 5. Clean backend thumbnails
for f in os.listdir('c:/m/backend/static/thumbnails'):
    fp = os.path.join('c:/m/backend/static/thumbnails', f)
    if os.path.isfile(fp) and f not in KEEP_THUMBS:
        print('Removing from backend/static/thumbnails:', f)
        try:
            os.remove(fp)
        except Exception as e:
            print('Error removing:', fp, e)

# 6. Clean frontend thumbnails
for f in os.listdir('c:/m/frontend/public/static/thumbnails'):
    fp = os.path.join('c:/m/frontend/public/static/thumbnails', f)
    if os.path.isfile(fp) and f not in KEEP_THUMBS:
        print('Removing from frontend/public/static/thumbnails:', f)
        try:
            os.remove(fp)
        except Exception as e:
            print('Error removing:', fp, e)

if os.path.exists('c:/m/frontend/dist/static/thumbnails'):
    for f in os.listdir('c:/m/frontend/dist/static/thumbnails'):
        fp = os.path.join('c:/m/frontend/dist/static/thumbnails', f)
        if os.path.isfile(fp) and f not in KEEP_THUMBS:
            print('Removing from frontend/dist/static/thumbnails:', f)
            try:
                os.remove(fp)
            except Exception as e:
                print('Error removing:', fp, e)

# 7. Clean subtitles
for d in ['c:/m/backend/static/subtitles', 'c:/m/frontend/public/static/subtitles', 'c:/m/frontend/dist/static/subtitles', 'c:/m/output/subtitles']:
    if os.path.exists(d):
        for f in os.listdir(d):
            fp = os.path.join(d, f)
            if os.path.isfile(fp) and f not in KEEP_SUBS:
                print('Removing subtitle:', fp)
                try:
                    os.remove(fp)
                except Exception as e:
                    print('Error removing:', fp, e)

# 8. Clean audio
if os.path.exists('c:/m/backend/static/audio'):
    for f in os.listdir('c:/m/backend/static/audio'):
        fp = os.path.join('c:/m/backend/static/audio', f)
        if os.path.isfile(fp) and f not in KEEP_AUDIO:
            print('Removing audio:', f)
            try:
                os.remove(fp)
            except Exception as e:
                print('Error removing:', fp, e)

# 9. Clean database
db_path = 'c:/m/backend/data/mysteryverse.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("DELETE FROM video_jobs WHERE id NOT IN ('mysteryverse_intro_short', 'mysteryverse_intro_long')")
    c.execute("DELETE FROM channel_uploads WHERE video_job_id NOT IN ('mysteryverse_intro_short', 'mysteryverse_intro_long')")
    conn.commit()
    conn.close()
    print('Database cleaned: Only mysteryverse_intro_short and mysteryverse_intro_long remain.')

print('ALL OTHER VIDEOS REMOVED SUCCESSFULLY!')
