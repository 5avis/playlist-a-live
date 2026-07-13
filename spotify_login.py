import spotipy
from spotipy.oauth2 import SpotifyOAuth

CLIENT_ID = "f378884933fd40419ed4ceb4183187fa"
CLIENT_SECRET = "0fe835117c40467f87b7fa6f168d56dc"   # fill this in
REDIRECT_URI = "http://127.0.0.1:8888/callback"

SCOPE = (
    "playlist-read-private "
    "playlist-read-collaborative "
    "playlist-modify-public "
    "playlist-modify-private"
)

sp_oauth = SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope=SCOPE,
    open_browser=True,
    cache_path=".cache"
)

print("Opening browser for authorization...")
auth_url = sp_oauth.get_authorize_url()
print(auth_url)

# use get_cached_token / get_access_token without as_dict (deprecated)
token_info = sp_oauth.get_access_token(as_dict=False)

sp = spotipy.Spotify(auth=token_info)

user = sp.current_user()
print(f"Logged in as: {user['display_name']} ({user['id']})")