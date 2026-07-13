import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

# Load features
print("📋 Loading tracks_with_features.csv...\n")
df = pd.read_csv('tracks_with_features.csv')
print(f"✅ Loaded {len(df)} tracks\n")

# Features to cluster on
features = ['popularity', 'rank_score', 'popularity_tier', 
            'duration_sec', 'explicit', 'trend_score']

X = df[features]

# Scale the features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# ── Elbow Method (find best K) ──────────────────────────────
print("📊 Running elbow method to find best K...\n")
inertias = []
K_range = range(2, 9)

for k in K_range:
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    km.fit(X_scaled)
    inertias.append(km.inertia_)

# Plot elbow curve
plt.figure(figsize=(8, 4))
plt.plot(list(K_range), inertias, 'bo-')
plt.xlabel('Number of Clusters (K)')
plt.ylabel('Inertia')
plt.title('Elbow Method — Find Best K')
plt.savefig('elbow_curve.png')
print("✅ Elbow curve saved as elbow_curve.png\n")

# ── Silhouette Score (evaluate best K) ──────────────────────
print("📊 Running silhouette scores...\n")
best_k = 2
best_score = -1

for k in K_range:
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = km.fit_predict(X_scaled)
    score = silhouette_score(X_scaled, labels)
    print(f"  K={k} → Silhouette Score: {round(score, 4)}")
    if score > best_score:
        best_score = score
        best_k = k

print(f"\n✅ Best K = {best_k} (Silhouette Score: {round(best_score, 4)})\n")

# ── Final Clustering with Best K ────────────────────────────
print(f"🤖 Running final K-Means with K={best_k}...\n")
final_km = KMeans(n_clusters=best_k, random_state=42, n_init=10)
df['cluster'] = final_km.fit_predict(X_scaled)

# Show cluster breakdown
print("📊 Cluster breakdown:\n")
for c in range(best_k):
    cluster_df = df[df['cluster'] == c]
    avg_pop = round(cluster_df['popularity'].mean(), 1)
    print(f"  Cluster {c}: {len(cluster_df)} songs | Avg Popularity: {avg_pop}")
    for _, row in cluster_df.iterrows():
        print(f"    - {row['track_name']} ({row['artist']})")
    print()

# Save clustered CSV
df.to_csv('tracks_clustered.csv', index=False)
print("✅ Saved to tracks_clustered.csv")
print(f"✅ Silhouette Score: {round(best_score, 4)} (closer to 1.0 = better clustering)")