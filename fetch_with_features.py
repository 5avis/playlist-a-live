import csv
import math

print("📋 Loading tracks from trending_tracks.csv...\n")

tracks = []
with open('trending_tracks.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        tracks.append(row)

total_tracks = max(1, len(tracks))
print(f"✅ Loaded {total_tracks} unique candidate tracks\n")

enriched_tracks = []

for track in tracks:
    popularity = float(track.get('popularity', 50))
    rank = int(track.get('rank', total_tracks))
    duration_sec = float(track.get('duration_sec') or 210)
    explicit = int(track.get('explicit') or 0)
    in_playlist = int(track.get('in_playlist') or 0)

    # 1. Rank Score (0 to 1)
    rank_score = round(1 - (rank / total_tracks), 4)

    # 2. Duration Score: Gaussian bell-curve around 210s (3.5 mins) with standard dev 80s
    duration_score = round(math.exp(-0.5 * ((duration_sec - 210) / 80) ** 2), 4)

    # 3. Popularity Tier
    if popularity >= 85:
        popularity_tier = 2
    elif popularity >= 70:
        popularity_tier = 1
    else:
        popularity_tier = 0

    # 4. Multi-factor Trend Composite Score
    # 50% popularity + 35% rank velocity + 15% optimal duration
    trend_score = round((0.50 * (popularity / 100)) + (0.35 * rank_score) + (0.15 * duration_score), 4)

    # 5. Stability boost for existing playlist songs (+0.04)
    if in_playlist == 1:
        trend_score = round(min(1.0, trend_score + 0.04), 4)

    enriched = {
        'rank': rank,
        'track_id': track['track_id'],
        'track_name': track['track_name'],
        'artist': track['artist'],
        'clean_key': track.get('clean_key', ''),
        'popularity': int(popularity),
        'rank_score': rank_score,
        'popularity_tier': popularity_tier,
        'duration_sec': round(duration_sec, 1),
        'duration_score': duration_score,
        'explicit': explicit,
        'in_playlist': in_playlist,
        'trend_score': trend_score
    }
    enriched_tracks.append(enriched)

fields = [
    'rank', 'track_id', 'track_name', 'artist', 'clean_key', 'popularity',
    'rank_score', 'popularity_tier', 'duration_sec', 'duration_score',
    'explicit', 'in_playlist', 'trend_score'
]

with open('tracks_with_features.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(enriched_tracks)

print(f"✅ Total enriched: {len(enriched_tracks)} tracks")
print("✅ Saved to tracks_with_features.csv")
