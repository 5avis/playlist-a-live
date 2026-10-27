import csv
import re
import math
import os
from ytmusicapi import YTMusic

YOUR_PLAYLIST_ID = os.getenv("YT_PLAYLIST_ID", "PLQZ2bR5J0yDY")

print("🎵 Initializing YouTube Music API...")
if os.path.exists('browser.json'):
    yt = YTMusic('browser.json')
    print("✅ Using authenticated session (browser.json)")
else:
    yt = YTMusic()
    print("ℹ️  Using public session (no login required for search)")

def clean_name(text):
    if not text:
        return ""
    t = re.sub(r'\(.*?\)', '', text)
    t = re.sub(r'\[.*?\]', '', t)
    t = re.sub(r'\|.*', '', t)
    t = re.sub(r'ft\..*|feat\..*', '', t, flags=re.IGNORECASE)
    t = re.sub(r'[^a-zA-Z0-9\s]', '', t)
    return ' '.join(t.split()).strip().lower()

def parse_views_to_popularity(v, rank_in_results=0):
    if not v:
        return max(40, 95 - (rank_in_results * 2))
    v_str = str(v).strip().upper()
    try:
        if 'B' in v_str:
            num = float(re.sub(r'[^0-9.]', '', v_str)) * 1_000_000_000
        elif 'M' in v_str:
            num = float(re.sub(r'[^0-9.]', '', v_str)) * 1_000_000
        elif 'K' in v_str:
            num = float(re.sub(r'[^0-9.]', '', v_str)) * 1_000
        else:
            digits = re.sub(r'[^0-9]', '', v_str)
            num = float(digits) if digits else 1_000_000
    except Exception:
        num = 1_000_000

    if num <= 0:
        return 40
    pop = int(20 + 8 * math.log10(max(10_000, num)))
    return min(100, max(30, pop))

# 1. Fetch current playlist tracks so they participate in re-ranking tournament
playlist_tracks = {}
if os.path.exists('browser.json'):
    try:
        print(f"📋 Fetching current playlist tracks from {YOUR_PLAYLIST_ID}...")
        pl = yt.get_playlist(YOUR_PLAYLIST_ID)
        for item in pl.get('tracks', []):
            vid = item.get('videoId')
            if vid:
                title = item.get('title', 'Unknown')
                artist = item.get('artists', [{}])[0].get('name', 'Unknown')
                key = f"{clean_name(title)}---{clean_name(artist)}"
                playlist_tracks[vid] = {
                    'track_id': vid,
                    'track_name': title,
                    'artist': artist,
                    'clean_key': key,
                    'popularity': 85,  # Baseline loyalty score for current tracks
                    'duration_sec': item.get('duration_seconds') or 210,
                    'explicit': 0,
                    'in_playlist': 1
                }
        print(f"✅ Found {len(playlist_tracks)} tracks currently in playlist")
    except Exception as e:
        print(f"⚠️  Could not read current playlist: {e}")

# 2. Search broad trending categories
search_queries = [
    "top hits 2026", "best songs 2026", "trending music 2026",
    "viral songs 2026", "pop hits 2026", "hip hop 2026",
    "indie hits 2026", "tamil hits 2026", "bollywood hits 2026",
    "global hits 2026", "new music 2026", "chart hits 2026",
]

print("\n🎵 Searching trending tracks across multi-genre categories...")
candidate_dict = {}

# Seed with current playlist tracks
for vid, data in playlist_tracks.items():
    candidate_dict[data['clean_key']] = data

for query in search_queries:
    try:
        results = yt.search(query, filter='songs', limit=15)
    except Exception as e:
        print(f"⚠️  Query '{query}' error: {e}")
        continue

    for idx, item in enumerate(results):
        vid = item.get('videoId')
        if not vid:
            continue
        title = item.get('title', 'Unknown')
        artist = item.get('artists', [{}])[0].get('name', 'Unknown') if item.get('artists') else 'Unknown'
        key = f"{clean_name(title)}---{clean_name(artist)}"
        pop = parse_views_to_popularity(item.get('views'), idx)
        duration = item.get('duration_seconds') or 210
        explicit = 1 if item.get('isExplicit') else 0

        # Deduplication rule: If we already have this song, update if this version has higher popularity
        if key in candidate_dict:
            if pop > candidate_dict[key]['popularity']:
                candidate_dict[key]['popularity'] = pop
                candidate_dict[key]['track_id'] = vid
        else:
            candidate_dict[key] = {
                'track_id': vid,
                'track_name': title,
                'artist': artist,
                'clean_key': key,
                'popularity': pop,
                'duration_sec': duration,
                'explicit': explicit,
                'in_playlist': 1 if vid in playlist_tracks else 0
            }

    if len(candidate_dict) >= 120:
        break

# Sort all candidates by popularity
all_candidates = sorted(candidate_dict.values(), key=lambda x: x['popularity'], reverse=True)

# Assign initial ranks
for i, track in enumerate(all_candidates):
    track['rank'] = i + 1

print(f"\n✅ Total unique deduplicated candidates gathered: {len(all_candidates)}")

fields = ['rank', 'track_id', 'track_name', 'artist', 'clean_key', 'popularity', 'duration_sec', 'explicit', 'in_playlist']
with open('trending_tracks.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(all_candidates)

print("✅ Saved to trending_tracks.csv")
