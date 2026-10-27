# playlist-a-live

Automated daily pipeline that curates and updates a YouTube Music playlist with the latest trending songs using K-Means ML clustering and GitHub Actions.

## Pipeline Stages
- **Stage 4 — Fetch Trending** (`fetch_trending.py`): Queries YouTube Music for trending tracks, parses views, and scores popularity.
- **Stage 5 — Feature Engineer** (`fetch_with_features.py`): Computes ranking, popularity tiers, and trend scores.
- **Stage 6 — Clustering** (`clustering.py`): Applies K-Means clustering with Scikit-Learn to cluster songs.
- **Stage 7 — Decisions** (`decision.py`): Selects top cluster tracks to add and removes non-trending tracks.
- **Stage 8 — Update Playlist** (`update_playlist.py`): Updates YouTube Music playlist via `ytmusicapi`.
- **Stage 9 — Activity Log** (`activity_log.py`): Appends decisions to `activity_log.csv`.

## GitHub Actions Automation
Runs daily at 00:00 UTC via `.github/workflows/daily.yml`.
Required GitHub Secrets:
- `YTM_BROWSER_JSON`: Content of `browser.json`
- `YT_PLAYLIST_ID`: Your YouTube playlist ID (`PLQZ2bR5J0yDY`)
