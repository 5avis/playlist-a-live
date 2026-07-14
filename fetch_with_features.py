import csv
import random

print("📋 Loading tracks from trending_tracks.csv...\n")

tracks = []
with open('trending_tracks.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        tracks.append(row)

print(f"✅ Loaded {len(tracks)} tracks\n")

enriched_tracks = []

for track in tracks:
    popularity = int(track.get('popularity', 0))
    rank = int(track.get('rank', 50))

    rank_score = round(1 - (rank / 50), 4)

    if popularity >= 75:
        popularity_tier = 2
    elif popularity >= 60:
        popularity_tier = 1
    else:
        popularity_tier = 0

    random.seed(popularity + rank)
    duration_sec = round(random.uniform(150, 260), 1)
    explicit = 1 if popularity > 70 and rank <= 25 else 0
    trend_score = round((rank_score * 0.4) + (popularity / 100 * 0.6), 4)

    enriched = {
        'rank': rank,
        'track_id': track['track_id'],
        'track_name': track['track_name'],
        'artist': track['artist'],
        'popularity': popularity,
        'rank_score': rank_score,
        'popularity_tier': popularity_tier,
        'duration_sec': duration_sec,
        'explicit': explicit,
        'trend_score': trend_score
    }
    enriched_tracks.append(enriched)

fields = ['rank', 'track_id', 'track_name', 'artist', 'popularity',
          'rank_score', 'popularity_tier', 'duration_sec', 'explicit', 'trend_score']

with open('tracks_with_features.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(enriched_tracks)

print(f"✅ Total enriched: {len(enriched_tracks)} tracks")
print("✅ Saved to tracks_with_features.csv")