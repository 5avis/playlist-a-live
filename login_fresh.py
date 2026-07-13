import spotipy
from spotipy.oauth2 import SpotifyOAuth

CLIENT_ID     = "f378884933fd40419ed4ceb4183187fa"
CLIENT_SECRET = "0fe835117c40467f87b7fa6f168d56dc"
REDIRECT_URI  = "http://127.0.0.1:8888/callback"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope="playlist-read-private",
    cache_path=".cache"
))

user = sp.current_user()
print(f"✅ Connected as: {user['display_name']}")
playlists = sp.current_user_playlists()
for p in playlists['items']:
    print(f"  - {p['name']}")
