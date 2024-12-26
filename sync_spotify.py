import logging, requests

BEARER_TOKEN = ""


def get_bearer_token():
    try:
        CLIENT_ID = "e91218f06acf4549b91aa7053c8d1b8b"
        CLIENT_SECRET = "3c4485af7c4b4413918417704b5ca634"
        REDIRECT_URI = "http://localhost:8888/callback"
        AUTHORIZATION_CODE = "code_from_redirect"

        url = "https://accounts.spotify.com/api/token"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "grant_type": "authorization_code",
            "code": AUTHORIZATION_CODE,
            "redirect_uri": REDIRECT_URI,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        }
        response = requests.post(url, headers=headers, data=data)
        token_info = response.json()

        # Extract the Bearer Token
        bearer_token = token_info.get("access_token")
        return bearer_token
    except Exception as err:
        logging.error("API_ERROR(SYNC_SPOTIFY) " + str(err))
        return None


def fetch_liked_songs(limit=20, offset=0):
    url = "https://api.spotify.com/v1/me/tracks"
    headers = {"Authorization": f"Basic {BEARER_TOKEN}"}
    params = {"limit": limit, "offset": offset}

    # Send GET request to Spotify API
    response = requests.get(url, headers=headers, params=params)

    # Check for errors
    if response.status_code != 200:
        print(f"Error: {response.status_code}, {response.json()}")
        return []

    # Extract and return track data
    data = response.json()
    tracks = []
    for item in data["items"]:
        track = item["track"]
        tracks.append(
            {
                "name": track["name"],
                "artist": ", ".join(artist["name"] for artist in track["artists"]),
                "album": track["album"]["name"],
                "id": track["id"],
                "uri": track["uri"],
            }
        )
    return tracks


# Example Usage
liked_songs = fetch_liked_songs(limit=10)  # Fetch first 10 tracks
for song in liked_songs:
    print(f"{song['name']} by {song['artist']} (Album: {song['album']})")


def fetch_all_liked_songs():
    all_tracks = []
    offset = 0
    limit = 50  # Maximum allowed by Spotify API
    while True:
        tracks = fetch_liked_songs(limit=limit, offset=offset)
        if not tracks:
            break
        all_tracks.extend(tracks)
        offset += limit
    return all_tracks


# Example Usage
all_liked_songs = fetch_all_liked_songs()
print(f"Total liked songs: {len(all_liked_songs)}")

if __name__ == "__main__":
    token = get_bearer_token()
    # fetch_all_liked_songs()
