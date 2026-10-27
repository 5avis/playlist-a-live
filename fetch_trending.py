from ytmusicapi import YTMusic
import csv
import re
import math
import os

print("🎵 Initializing YouTube Music API...")
# Use authenticated instance if browser.json exists, otherwise unauthenticated
if os.path.exists('browser.json'):
    yt = YTMusic('browser.json')
    print("✅ Using authenticated session (browser.json)")
else:
    yt = YTMusic()
    print("ℹ️  Using public session (no login required for search)")

print("\n🎵 Searching for trending songs on YouTube Music...\n")

search_queries = [
    "top hits 2026", "best songs 2026", "trending music 2026",
    "viral songs 2026", "pop hits 2026", "hip hop 2026",
    "indie hits 2026", "tamil hits 2026", "bollywood hits 2026",
    "global hits 2026", "new music 2026", "chart hits 2026",
]

def parse_views_to_popularity(v, rank_in_results=0):
    """Convert view string (e.g. '13M', '1.1B') into a 0-100 popularity score."""
    if not v:
        # Fall back to ranking position
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

    # Logarithmic scaling between 40 and 100
    if num <= 0:
        return 40
    pop = int(20 + 8 * math.log10(max(10_000, num)))
    return min(100, max(30, pop))

def fetch_songs(min_popularity=0):
    tracks = []
    seen_ids = set()
    for query in search_queries:
        try:
            results = yt.search(query, filter='songs', limit=15)
        except Exception as e:
            print(f"⚠️  Query '{query}' error: {e}")
            continue

        for idx, item in enumerate(results):
            vid = item.get('videoId')
            if vid and vid not in seen_ids:
                seen_ids.add(vid)
                popularity = parse_views_to_popularity(item.get('views'), idx)
                if popularity >= min_popularity:
                    artists = item.get('artists')
                    artist_name = artists[0]['name'] if (artists and len(artists) > 0) else 'Unknown'
                    track_info = {
                        'rank': len(tracks) + 1,
                        'track_id': vid,
                        'track_name': item.get('title', 'Unknown'),
                        'artist': artist_name,
                        'popularity': popularity,
                        'duration_sec': item.get('duration_seconds') or 200,
                        'explicit': 1 if item.get('isExplicit') else 0
                    }
                    tracks.append(track_info)
                    print(f"{len(tracks)}. {track_info['track_name']} — {track_info['artist']} (Popularity: {popularity})")
        if len(tracks) >= 100:
            break
    return tracks

print("🔍 Fetching songs with popularity 60+...\n")
tracks = fetch_songs(min_popularity=60)

if len(tracks) < 10:
    print("\n⚠️  Too few songs found, trying popularity 40+...\n")
    tracks = fetch_songs(min_popularity=40)

if len(tracks) < 10:
    print("\n⚠️  Still too few, fetching all songs...\n")
    tracks = fetch_songs(min_popularity=0)

# Sort by popularity — best songs rise to top
tracks = sorted(tracks, key=lambda x: x['popularity'], reverse=True)

# Keep top 50
tracks = tracks[:50]

# Re-rank
for i, track in enumerate(tracks):
    track['rank'] = i + 1

print(f"\n✅ Total tracks fetched: {len(tracks)}")

with open('trending_tracks.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['rank', 'track_id', 'track_name', 'artist', 'popularity', 'duration_sec', 'explicit'])
    writer.writeheader()
    writer.writerows(tracks)

print("✅ Saved to trending_tracks.csv")
