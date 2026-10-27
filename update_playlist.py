import os
import sys
import pandas as pd
from ytmusicapi import YTMusic

YOUR_PLAYLIST_ID = os.getenv("YT_PLAYLIST_ID", "PLQZ2bR5J0yDY")

if not os.path.exists('browser.json'):
    print("⚠️  browser.json not found. Please run yt_auth.py first or provide browser.json.")
    sys.exit(1)

yt = YTMusic('browser.json')
print("✅ Connected to YouTube Music\n")

if not os.path.exists('decisions.csv'):
    print("⚠️  decisions.csv not found.")
    sys.exit(1)

decisions = pd.read_csv('decisions.csv')
to_add_rows = decisions[decisions['action'] == 'ADD']
to_remove_rows = decisions[decisions['action'] == 'REMOVE']

to_add = to_add_rows['track_id'].tolist()
to_remove = to_remove_rows['track_id'].tolist()

print(f"➕ Songs to add:    {len(to_add)}")
print(f"➖ Songs to remove: {len(to_remove)}\n")

# REMOVE songs
if to_remove:
    print("🗑️  Removing songs from playlist...")
    try:
        playlist = yt.get_playlist(YOUR_PLAYLIST_ID)
        items_to_remove = []
        for track in playlist.get('tracks', []):
            if track.get('videoId') in to_remove and track.get('setVideoId'):
                items_to_remove.append({
                    'videoId': track['videoId'],
                    'setVideoId': track['setVideoId']
                })
        if items_to_remove:
            yt.remove_playlist_items(YOUR_PLAYLIST_ID, items_to_remove)
            print(f"✅ Removed {len(items_to_remove)} tracks from playlist!")
            for tid in to_remove:
                match = decisions[decisions['track_id'] == tid]
                if not match.empty:
                    print(f"  - {match.iloc[0]['track_name']} — {match.iloc[0]['artist']}")
    except Exception as e:
        print(f"⚠️  Error removing songs: {e}")
else:
    print("ℹ️  No songs to remove.")

# ADD songs
if to_add:
    print("\n➕ Adding songs to playlist...")
    try:
        yt.add_playlist_items(YOUR_PLAYLIST_ID, to_add, duplicates=False)
        print("✅ Songs added to playlist!")
        for tid in to_add:
            match = decisions[decisions['track_id'] == tid]
            if not match.empty:
                print(f"  + {match.iloc[0]['track_name']} — {match.iloc[0]['artist']}")
    except Exception as e:
        print(f"⚠️  Error adding songs: {e}")
else:
    print("ℹ️  No songs to add.")

print("\n🎉 YouTube Music playlist updated successfully!")
