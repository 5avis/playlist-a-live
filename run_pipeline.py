import subprocess
import sys

print("🚀 PLAYLIVE Pipeline Starting (YouTube Music)...\n")

scripts = [
    ("Stage 4 — Fetch Trending",   "fetch_trending.py"),
    ("Stage 5 — Feature Engineer", "fetch_with_features.py"),
    ("Stage 6 — Clustering",       "clustering.py"),
    ("Stage 7 — Decisions",        "decision.py"),
    ("Stage 8 — Update Playlist",  "update_playlist.py"),
    ("Stage 9 — Activity Log",     "activity_log.py"),
]

for stage_name, script in scripts:
    print(f"▶️  Running {stage_name}...")
    result = subprocess.run([sys.executable, script], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ {stage_name} failed!")
        print(result.stderr)
        print(result.stdout)
        sys.exit(1)
    else:
        print(f"✅ {stage_name} done!\n")

print("🎉 Pipeline completed successfully!")
