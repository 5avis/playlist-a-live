import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyOAuth

CLIENT_ID        = "f378884933fd40419ed4ceb4183187fa"
CLIENT_SECRET    = "0fe835117c40467f87b7fa6f168d56dc"
REDIRECT_URI     = "http://127.0.0.1:8888/callback"
YOUR_PLAYLIST_ID = "6d2IqN9qIankzqBAx0qpXb"
SCOPE = "playlist-modify-public"

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
try:
    results = sp.playlist_tracks(YOUR_PLAYLIST_ID)
    current_tracks = []
    for i, item in enumerate(results['items']):
        track = item['track']
        if track:
            current_tracks.append({
                'track_id': track['id'],
                'track_name': track['name'],
                'artist': track['artists'][0]['name'],
                'days_in_playlist': i + 1
            })
    print(f"✅ {len(current_tracks)} tracks currently in your playlist\n")
except Exception as e:
    print(f"⚠️  Playlist empty or error: {e}")
    current_tracks = []

current_ids  = set(t['track_id'] for t in current_tracks)
trending_ids = set(trending_df['track_id'].tolist())

# Decision logic
print("🤖 Running add/remove decision logic...\n")

best_cluster = trending_df.groupby('cluster')['popularity'].mean().idxmax()
print(f"✅ Best cluster selected: Cluster {best_cluster}\n")

best_cluster_tracks = trending_df[trending_df['cluster'] == best_cluster]
to_add = best_cluster_tracks[
    ~best_cluster_tracks['track_id'].isin(current_ids)
].head(50)

to_remove = [t for t in current_tracks if t['track_id'] not in trending_ids]

# Print decisions
print("➕ SONGS TO ADD:")
if len(to_add) == 0:
    print("  None — all trending songs already in playlist!\n")
else:
    for _, row in to_add.iterrows():
        print(f"  + {row['track_name']} — {row['artist']} (Cluster {row['cluster']}, Popularity: {row['popularity']})")

print(f"\n➖ SONGS TO REMOVE:")
if len(to_remove) == 0:
    print("  None — all playlist songs are still trending!\n")
else:
    for t in to_remove:
        print(f"  - {t['track_name']} — {t['artist']}")

# Save decisions
to_add_list = to_add[['track_id', 'track_name', 'artist', 'cluster', 'popularity']].copy()
to_add_list['action'] = 'ADD'

to_remove_list = pd.DataFrame(to_remove)
if len(to_remove_list) > 0:
    to_remove_list['action'] = 'REMOVE'
    to_remove_list['cluster'] = -1
    to_remove_list = to_remove_list[['track_id', 'track_name', 'artist', 'cluster', 'action']]

all_decisions = pd.concat([
    to_add_list,
    to_remove_list if len(to_remove_list) > 0 else pd.DataFrame()
], ignore_index=True)

all_decisions.to_csv('decisions.csv', index=False)
print(f"\n✅ Decisions saved to decisions.csv")
print(f"   ➕ {len(to_add)} songs to add")
print(f"   ➖ {len(to_remove)} songs to remove")