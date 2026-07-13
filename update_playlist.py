import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd

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

# Load decisions
decisions = pd.read_csv('decisions.csv')
to_add    = decisions[decisions['action'] == 'ADD']['track_id'].tolist()
to_remove = decisions[decisions['action'] == 'REMOVE']['track_id'].tolist()

print(f"➕ Songs to add:    {len(to_add)}")
print(f"➖ Songs to remove: {len(to_remove)}\n")

# ADD songs
if to_add:
    sp.playlist_add_items(YOUR_PLAYLIST_ID, to_add)
    print("✅ Songs added to playlist!")
    for tid in to_add:
        row = decisions[decisions['track_id'] == tid].iloc[0]
        print(f"  + {row['track_name']} — {row['artist']}")
else:
    print("ℹ️  No songs to add.")

# REMOVE songs
if to_remove:
    sp.playlist_remove_all_occurrences_of_items(YOUR_PLAYLIST_ID, to_remove)
    print("\n✅ Songs removed from playlist!")
    for tid in to_remove:
        row = decisions[decisions['track_id'] == tid].iloc[0]
        print(f"  - {row['track_name']} — {row['artist']}")
else:
    print("ℹ️  No songs to remove.")

print("\n🎉 Playlist updated successfully!")