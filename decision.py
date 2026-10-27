import pandas as pd
from ytmusicapi import YTMusic
import os
import sys

YOUR_PLAYLIST_ID = os.getenv("YT_PLAYLIST_ID", "PLQZ2bR5J0yDY")

if not os.path.exists('browser.json'):
    print("⚠️  browser.json not found. Please run yt_auth.py first or provide browser.json.")
    sys.exit(1)

yt = YTMusic('browser.json')
print("✅ Connected to YouTube Music\n")

# Load clustered trending songs
print("📋 Loading clustered trending tracks...\n")
trending_df = pd.read_csv('tracks_clustered.csv')
print(f"✅ {len(trending_df)} trending tracks loaded\n")

# Get current playlist tracks
print("📋 Fetching your current PLAYLIVE YouTube playlist...\n")
current_tracks = []
try:
    playlist = yt.get_playlist(YOUR_PLAYLIST_ID)
    seen_in_playlist = set()
    for item in playlist.get('tracks', []):
        vid = item.get('videoId')
        if vid and vid not in seen_in_playlist:
            seen_in_playlist.add(vid)
            artists = item.get('artists')
            artist_name = artists[0]['name'] if (artists and len(artists) > 0) else 'Unknown'
            current_tracks.append({
                'track_id': vid,
                'set_video_id': item.get('setVideoId', ''),
                'track_name': item.get('title', 'Unknown'),
                'artist': artist_name,
                'popularity': 80
            })
    print(f"✅ {len(current_tracks)} tracks currently in playlist\n")
except Exception as e:
    print(f"⚠️  Could not fetch playlist: {e}")
    current_tracks = []

current_ids = set(t['track_id'] for t in current_tracks)
trending_ids = set(trending_df['track_id'].tolist())

# Decision logic
print("🤖 Running add/remove decision logic...\n")

# REMOVE songs that are no longer trending
to_remove = [
    t for t in current_tracks
    if t['track_id'] not in trending_ids
]
print(f"➖ Songs to remove (not trending): {len(to_remove)}")
for t in to_remove:
    print(f"  - {t['track_name']} — {t['artist']}")

# Available slots
MAX_PLAYLIST_SIZE = 50
current_count = len(current_ids) - len(to_remove)
slots_available = max(0, MAX_PLAYLIST_SIZE - current_count)

# ADD songs from best cluster
best_cluster = trending_df.groupby('cluster')['popularity'].mean().idxmax()
print(f"\n✅ Best cluster: Cluster {best_cluster}")

best_cluster_tracks = trending_df[trending_df['cluster'] == best_cluster]
to_add = best_cluster_tracks[
    ~best_cluster_tracks['track_id'].isin(current_ids)
].head(slots_available)

print(f"➕ Songs to add: {len(to_add)}")
for _, row in to_add.iterrows():
    print(f"  + {row['track_name']} — {row['artist']} (Popularity: {row['popularity']})")

# Save decisions
decisions = []
for t in to_remove:
    decisions.append({
        'action': 'REMOVE',
        'track_id': t['track_id'],
        'track_name': t['track_name'],
        'artist': t['artist'],
        'cluster': '-',
        'popularity': t['popularity']
    })

for _, row in to_add.iterrows():
    decisions.append({
        'action': 'ADD',
        'track_id': row['track_id'],
        'track_name': row['track_name'],
        'artist': row['artist'],
        'cluster': row['cluster'],
        'popularity': row['popularity']
    })

decisions_df = pd.DataFrame(decisions)
decisions_df.to_csv('decisions.csv', index=False)
print("\n✅ Saved decisions to decisions.csv")
