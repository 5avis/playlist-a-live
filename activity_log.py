import pandas as pd
import csv
import os
from datetime import datetime

# Load today's decisions
decisions = pd.read_csv('decisions.csv')

log_file = 'activity_log.csv'

# Create log file with headers if it doesn't exist
if not os.path.exists(log_file):
    with open(log_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['date', 'track_name', 'artist', 'action', 'cluster', 'popularity'])

# Append today's decisions
with open(log_file, 'a', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    for _, row in decisions.iterrows():
        writer.writerow([
            datetime.now().strftime('%Y-%m-%d %H:%M'),
            row['track_name'],
            row['artist'],
            row['action'],
            row.get('cluster', '-'),
            row.get('popularity', '-')
        ])

print("📋 Activity Log — What happened today:\n")
log = pd.read_csv(log_file)
print(log.to_string(index=False))
print(f"\n✅ Saved to activity_log.csv")