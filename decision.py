import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyOAuth

CLIENT_ID        = "f378884933fd40419ed4ceb4183187fa"
CLIENT_SECRET    = "0fe835117c40467f87b7fa6f168d56dc"
REDIRECT_URI     = "http://127.0.0.1:8888/callback"
YOUR_PLAYLIST_ID = "6d2IqN9qIankzqBAx0qpXb"
SCOPE            = "playlist-modify-public"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope=SCOPE,
    cache_path=".cache"
))

user = sp.current_user()
print(f"✅ Connected as: {user['display_name']}\n")

# Load clustered trending songs
print("📋 Loading clustered trending tracks...\n")
trending_df = pd.read_csv('tracks_clustered.csv')
print(f"✅ {len(trending_df)} trending tracks loaded\n")

# Get current playlist tracks
print("📋 Fetching your current PLAYLIVE playlist...\n")
current_tracks = []
try:
    results = sp.playlist_items(YOUR_PLAYLIST_ID)
    seen_in_playlist = set()
    for item in results['items']:
        if item and item.get('track') and isinstance(item['track'], dict):
            track = item['track']
            track_id = track.get('id')
            if track_id and track_id not in seen_in_playlist:
                seen_in_playlist.add(track_id)
                current_tracks.append({
                    'track_id': track_id,
                    'track_name': track.get('name', 'Unknown'),
                    'artist': track['artists'][0]['name'] if track.get('artists') else 'Unknown',
                    'popularity': track.get('popularity', 0)
                })
    print(f"✅ {len(current_tracks)} tracks currently in playlist\n")
except Exception as e:
    print(f"⚠️  Could not fetch playlist: {e}")
    current_tracks = []

current_ids  = set(t['track_id'] for t in current_tracks)
trending_ids = set(trending_df['track_id'].tolist())

# Remove duplicates from playlist
print("🧹 Checking for duplicates...\n")
all_ids_in_playlist = []
try:
    results = sp.playlist_items(YOUR_PLAYLIST_ID)
    for item in results['items']:
        if item and item.get('track') and isinstance(item['track'], dict):
            all_ids_in_playlist.append(item['track'].get('id'))
except:
    pass

duplicate_ids = [tid for tid in set(all_ids_in_playlist) if all_ids_in_playlist.count(tid) > 1]
if duplicate_ids:
    print(f"🗑️  Removing {len(duplicate_ids)} duplicates...\n")
    sp.playlist_remove_all_occurrences_of_items(YOUR_PLAYLIST_ID, duplicate_ids)
    # Re-add once (keep one copy)
    sp.playlist_add_items(YOUR_PLAYLIST_ID, duplicate_ids)

# Decision logic
print("🤖 Running add/remove decision logic...\n")

# REMOVE songs that are no longer trending or low popularity
to_remove = [
    t for t in current_tracks
    if t['track_id'] not in trending_ids
]
print(f"➖ Songs to remove (not trending): {len(to_remove)}")
for t in to_remove:
    print(f"  - {t['track_name']} — {t['artist']}")

# How many slots available
MAX_PLAYLIST_SIZE = 50
current_count = len(current_ids) - len(to_remove)
slots_available = MAX_PLAYLIST_SIZE - current_count

# ADD songs from best cluster to fill up to 50
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
to_add_df = to_add[['track_id', 'track_name', 'artist', 'cluster', 'popularity']].copy()
to_add_df['action'] = 'ADD'

to_remove_df = pd.DataFrame(to_remove)
if len(to_remove_df) > 0:
    to_remove_df['action'] = 'REMOVE'
    to_remove_df['cluster'] = -1
    to_remove_df['popularity'] = to_remove_df.get('popularity', 0)
    to_remove_df = to_remove_df[['track_id', 'track_name', 'artist', 'cluster', 'popularity', 'action']]

all_decisions = pd.concat([
    to_add_df,
    to_remove_df if len(to_remove_df) > 0 else pd.DataFrame()
], ignore_index=True)

all_decisions.to_csv('decisions.csv', index=False)
print(f"\n✅ Decisions saved to decisions.csv")
print(f"   ➕ {len(to_add)} songs to add")
print(f"   ➖ {len(to_remove)} songs to remove")
print(f"   🎵 Playlist will have: {current_count + len(to_add)} songs after update")