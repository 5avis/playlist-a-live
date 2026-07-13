import spotipy
from spotipy.oauth2 import SpotifyOAuth
import csv

CLIENT_ID     = "f378884933fd40419ed4ceb4183187fa"
CLIENT_SECRET = "0fe835117c40467f87b7fa6f168d56dc"
REDIRECT_URI  = "http://127.0.0.1:8888/callback"
SCOPE         = "playlist-modify-public"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope=SCOPE,
    cache_path=".cache"
))

user = sp.current_user()
print(f"✅ Connected as: {user['display_name']}\n")

print("🎵 Searching for best songs from multiple sources...\n")

# Wide variety of search queries covering all genres and regions
search_queries = [
    "top hits 2026",
    "best songs 2026",
    "trending music 2026",
    "viral songs 2026",
    "pop hits 2026",
    "hip hop 2026",
    "indie hits 2026",
    "tamil hits 2026",
    "bollywood hits 2026",
    "global hits 2026",
    "new music 2026",
    "chart hits 2026",
]

tracks = []
seen_ids = set()

for query in search_queries:
    results = sp.search(q=query, type='track', limit=10, market='US')
    for item in results['tracks']['items']:
        if item['id'] not in seen_ids:
            seen_ids.add(item['id'])
            popularity = item.get('popularity', 0)
            track_info = {
                'rank': len(tracks) + 1,
                'track_id': item['id'],
                'track_name': item.get('name', 'Unknown'),
                'artist': item['artists'][0]['name'] if item.get('artists') else 'Unknown',
                'popularity': popularity
            }
            tracks.append(track_info)
            print(f"{len(tracks)}. {track_info['track_name']} — {track_info['artist']} (Popularity: {popularity})")

    if len(tracks) >= 100:
        break

# Sort by popularity — best songs rise to top
tracks = sorted(tracks, key=lambda x: x['popularity'], reverse=True)

# Keep top 50 only
tracks = tracks[:50]

# Re-rank
for i, track in enumerate(tracks):
    track['rank'] = i + 1

print(f"\n✅ Total tracks fetched: {len(tracks)}")

with open('trending_tracks.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['rank', 'track_id', 'track_name', 'artist', 'popularity'])
    writer.writeheader()
    writer.writerows(tracks)

print("✅ Saved to trending_tracks.csv")













