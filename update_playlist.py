import os
import sys
import pandas as pd
from ytmusicapi import YTMusic

YOUR_PLAYLIST_ID = os.getenv("YT_PLAYLIST_ID", "PLQZ2bR5J0yDY")

if not os.path.exists('browser.json'):
    print("⚠️  browser.json not found.")
    sys.exit(1)

yt = YTMusic('browser.json')
print(f"✅ Connected to YouTube Music (Target Playlist: {YOUR_PLAYLIST_ID})\n")

if not os.path.exists('decisions.csv'):
    print("⚠️  decisions.csv not found.")
    sys.exit(1)

decisions = pd.read_csv('decisions.csv')
if decisions.empty:
    print("ℹ️  No decisions to process. Playlist is already optimal.")
    sys.exit(0)

to_remove_rows = decisions[decisions['action'] == 'REMOVE']
to_add_rows = decisions[decisions['action'] == 'ADD']

print(f"➖ Songs marked for removal: {len(to_remove_rows)}")
print(f"➕ Songs marked for addition: {len(to_add_rows)}\n")

# 1. Execute REMOVALS first (clears space and removes duplicates)
if not to_remove_rows.empty:
    print("🗑️  Executing song removals...")
    items_to_remove = []
    
    # Use exact setVideoId whenever available
    for _, row in to_remove_rows.iterrows():
        set_vid = str(row.get('set_video_id', '')).strip()
        vid = str(row.get('track_id', '')).strip()
        if set_vid and set_vid != 'nan' and vid and vid != 'nan':
            items_to_remove.append({
                'videoId': vid,
                'setVideoId': set_vid
            })

    # If any removal row is missing setVideoId, fetch from playlist dynamically
    if len(items_to_remove) < len(to_remove_rows):
        pl_live = yt.get_playlist(YOUR_PLAYLIST_ID)
        vids_to_del = set(to_remove_rows['track_id'].tolist())
        for track in pl_live.get('tracks', []):
            if track.get('videoId') in vids_to_del and track.get('setVideoId'):
                entry = {'videoId': track['videoId'], 'setVideoId': track['setVideoId']}
                if entry not in items_to_remove:
                    items_to_remove.append(entry)

    if items_to_remove:
        # YouTube Music API allows removing items in batches
        try:
            yt.remove_playlist_items(YOUR_PLAYLIST_ID, items_to_remove)
            print(f"✅ Successfully removed {len(items_to_remove)} tracks (including any duplicates)!")
        except Exception as e:
            print(f"⚠️  Error removing tracks: {e}")
    else:
        print("ℹ️  No matching items needed deletion.")
else:
    print("ℹ️  Zero removals needed.")

# 2. Execute ADDITIONS
if not to_add_rows.empty:
    print("\n➕ Executing song additions...")
    to_add_ids = to_add_rows['track_id'].tolist()
    try:
        yt.add_playlist_items(YOUR_PLAYLIST_ID, to_add_ids, duplicates=False)
        print(f"✅ Successfully added {len(to_add_ids)} new qualifying tracks!")
        for _, row in to_add_rows.iterrows():
            print(f"   + {row['track_name']} — {row['artist']}")
    except Exception as e:
        print(f"⚠️  Error adding songs: {e}")
else:
    print("ℹ️  Zero additions needed.")

# 3. Final Verification
print("\n🔍 Verifying final playlist status...")
try:
    final_pl = yt.get_playlist(YOUR_PLAYLIST_ID)
    final_tracks = final_pl.get('tracks', [])
    print(f"🎉 Final Playlist Count: {len(final_tracks)} / 50 songs!")
    if len(final_tracks) > 50:
        print("⚠️  Warning: Playlist slightly exceeded 50, trimming excess...")
        excess = final_tracks[50:]
        excess_removals = [{'videoId': t['videoId'], 'setVideoId': t['setVideoId']} for t in excess if t.get('setVideoId')]
        yt.remove_playlist_items(YOUR_PLAYLIST_ID, excess_removals)
        print("✅ Trimmed back to exact 50 songs.")
except Exception as e:
    print(f"⚠️  Could not run post-check: {e}")

print("\n🎉 Playlist sync completed successfully!")
