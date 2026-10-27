import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

print("📋 Loading tracks_with_features.csv...\n")
df = pd.read_csv('tracks_with_features.csv')
print(f"✅ Loaded {len(df)} candidate tracks\n")

features = ['popularity', 'rank_score', 'popularity_tier', 'duration_score', 'trend_score']
X = df[features]

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# ── Dynamic K Optimization (Silhouette + Inertia) ────────────────
print("📊 Evaluating cluster cohesion across K=3 to 6...\n")
K_range = range(3, min(7, len(df)))
best_k = 3
best_score = -1
inertias = []

for k in K_range:
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = km.fit_predict(X_scaled)
    score = silhouette_score(X_scaled, labels)
    inertias.append(km.inertia_)
    print(f"  K={k} → Silhouette Score: {round(score, 4)}")
    if score > best_score:
        best_score = score
        best_k = k

# Save Elbow Plot
plt.figure(figsize=(7, 3.5))
plt.plot(list(K_range), inertias, 'ro-')
plt.xlabel('Number of Clusters (K)')
plt.ylabel('Inertia')
plt.title(f'Cluster Optimization (Best K={best_k}, Silhouette={round(best_score, 3)})')
plt.tight_layout()
plt.savefig('elbow_curve.png')
print(f"\n✅ Optimal K = {best_k} (Silhouette Score: {round(best_score, 4)})\n")

# ── Final KMeans Fit ─────────────────────────────────────────────
final_km = KMeans(n_clusters=best_k, random_state=42, n_init=10)
df['cluster'] = final_km.fit_predict(X_scaled)

# ── Cluster Quality Scoring ──────────────────────────────────────
# Rank clusters by composite quality (average trend_score & popularity)
cluster_scores = df.groupby('cluster').agg({
    'trend_score': 'mean',
    'popularity': 'mean',
    'track_id': 'count'
}).rename(columns={'track_id': 'count'})

cluster_scores['cluster_rank'] = cluster_scores['trend_score'].rank(ascending=False, method='min').astype(int)
print("📊 Cluster Rankings:")
for c_id, row in cluster_scores.iterrows():
    print(f"  Cluster {c_id}: {int(row['count'])} tracks | Avg Pop: {round(row['popularity'], 1)} | Rank: #{int(row['cluster_rank'])}")

# Map cluster rank back to dataframe
cluster_rank_map = cluster_scores['cluster_rank'].to_dict()
df['cluster_rank'] = df['cluster'].map(cluster_rank_map)

# Compute final composite score: 85% individual trend score + 15% cluster tier bonus
max_rank = best_k
df['composite_score'] = round(df['trend_score'] * 0.85 + ((max_rank - df['cluster_rank'] + 1) / max_rank * 0.15), 4)

# Sort globally by composite score
df = df.sort_values(by='composite_score', ascending=False).reset_index(drop=True)
df['final_rank'] = df.index + 1

# Save clustered CSV
df.to_csv('tracks_clustered.csv', index=False)
print("\n✅ Saved ranked tracks to tracks_clustered.csv")
