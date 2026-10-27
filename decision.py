import pandas as pd
from ytmusicapi import YTMusic
import os
import sys
import re

YOUR_PLAYLIST_ID = os.getenv("YT_PLAYLIST_ID", "PLQZ2bR5J0yDY")
MAX_PLAYLIST_SIZE = 50

if not os.path.exists('browser.json'):
    print("⚠️  browser.json not found. Please provide authentication.")
    sys.exit(1)

yt = YTMusic('browser.json')
print(f"✅ Connected to YouTube Music (Target Playlist: {YOUR_PLAYLIST_ID})\n")

def clean_name(text):
    if not text:
        return ""
    t = re.sub(r'\(.*?\)', '', text)
    t = re.sub(r'\[.*?\]', '', t)
    t = re.sub(r'\|.*', '', t)
    t = re.sub(r'ft\..*|feat\..*', '', t, flags=re.IGNORECASE)
    t = re.sub(r'[^a-zA-Z0-9\s]', '', t)
    return ' '.join(t.split()).strip().lower()

# 1. Fetch live playlist items
print("📋 Inspecting current playlist items and scanning for duplicates...")
raw_playlist = yt.get_playlist(YOUR_PLAYLIST_ID)
raw_items = raw_playlist.get('tracks', [])
print(f"✅ Total items physically in playlist: {len(raw_items)}\n")

# 2. Strict In-Playlist Deduplication (detecting both repeated videoIds and repeated titles)
seen_video_ids = set()
seen_song_keys = set()
current_active_tracks = []
duplicate_removals = []

for item in raw_items:
    vid = item.get('videoId')
    set_vid = item.get('setVideoId')
    title = item.get('title', 'Unknown')
    artist = item.get('artists', [{}])[0].get('name', 'Unknown') if item.get('artists') else 'Unknown'
    song_key = f"{clean_name(title)}---{clean_name(artist)}"

    if not vid or not set_vid:
        continue

    # If this video ID or song title was already seen in the playlist, mark THIS duplicate occurrence for deletion
    if vid in seen_video_ids or song_key in seen_song_keys:
        print(f"🗑️  Duplicate detected in playlist: '{title}' — '{artist}' (will remove duplicate instance)")
        duplicate_removals.append({
            'action': 'REMOVE',
            'track_id': vid,
            'set_video_id': set_vid,
            'track_name': title,
            'artist': artist,
            'reason': 'DUPLICATE'
        })
    else:
        seen_video_ids.add(vid)
        seen_song_keys.add(song_key)
        current_active_tracks.append({
            'track_id': vid,
            'set_video_id': set_vid,
            'track_name': title,
            'artist': artist,
            'clean_key': song_key
        })

print(f"✅ Unique songs currently in playlist: {len(current_active_tracks)}")
print(f"⚠️  Duplicates flagged for immediate removal: {len(duplicate_removals)}\n")

# 3. Load ranked candidate tracks from ML clustering
print("📋 Loading ranked candidates from tracks_clustered.csv...")
clustered_df = pd.read_csv('tracks_clustered.csv')

# Ensure candidates are deduplicated
clustered_df = clustered_df.drop_duplicates(subset=['track_id']).drop_duplicates(subset=['clean_key'])

# Select top 50 globally best tracks
target_top_50 = clustered_df.head(MAX_PLAYLIST_SIZE)
target_video_ids = set(target_top_50['track_id'].tolist())
target_song_keys = set(target_top_50['clean_key'].tolist())

print(f"🎯 Target optimal pool size: {len(target_top_50)} tracks\n")

# 4. Calculate Removals & Additions
to_remove = []
to_keep = []

# A current song is removed if it's no longer in the target top 50
for track in current_active_tracks:
    if track['track_id'] not in target_video_ids and track['clean_key'] not in target_song_keys:
        to_remove.append({
            'action': 'REMOVE',
            'track_id': track['track_id'],
            'set_video_id': track['set_video_id'],
            'track_name': track['track_name'],
            'artist': track['artist'],
            'reason': 'DROPPED_FROM_TOP_50'
        })
    else:
        to_keep.append(track)

# How many slots can we add without exceeding MAX_PLAYLIST_SIZE?
active_remaining = len(to_keep)
available_slots = max(0, MAX_PLAYLIST_SIZE - active_remaining)

current_keys_active = set(t['clean_key'] for t in to_keep)
current_vids_active = set(t['track_id'] for t in to_keep)

to_add = []
for _, row in target_top_50.iterrows():
    if row['track_id'] not in current_vids_active and row['clean_key'] not in current_keys_active:
        if len(to_add) < available_slots:
            to_add.append({
                'action': 'ADD',
                'track_id': row['track_id'],
                'set_video_id': '',
                'track_name': row['track_name'],
                'artist': row['artist'],
                'reason': 'NEW_QUALIFIER'
            })

# Combine all decisions
all_decisions = duplicate_removals + to_remove + to_add
decisions_df = pd.DataFrame(all_decisions)
decisions_df.to_csv('decisions.csv', index=False)

print("=" * 60)
print(f"📊 TOURNAMENT SUMMARY:")
print(f"  • Songs to keep:     {len(to_keep)}")
print(f"  • Songs to remove:   {len(to_remove) + len(duplicate_removals)} ({len(duplicate_removals)} duplicates, {len(to_remove)} dropped)")
print(f"  • New songs to add:  {len(to_add)}")
print(f"  • Projected total:   {len(to_keep) + len(to_add)} / {MAX_PLAYLIST_SIZE}")
print("=" * 60)

if to_remove:
    print("\n➖ Songs being removed:")
    for r in to_remove[:10]:
        print(f"   - {r['track_name']} — {r['artist']} ({r['reason']})")
    if len(to_remove) > 10:
        print(f"   ... and {len(to_remove) - 10} more")

if to_add:
    print("\n➕ Songs being added:")
    for a in to_add[:10]:
        print(f"   + {a['track_name']} — {a['artist']}")
    if len(to_add) > 10:
        print(f"   ... and {len(to_add) - 10} more")

print("\n✅ Saved decisions to decisions.csv")
