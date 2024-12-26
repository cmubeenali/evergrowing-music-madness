import logging, requests

BEARER_TOKEN = "AQA0XbjsW31iE0aBaQrBRI224usAtpuk9IJxXRoIuqVVHbamvyYYKMLBZY5k_eX08hFOPo_8wad1RqhQxVGqdEmhSuNCkTFoQ56YE8YIF-Co63EedDYKf6P__MUzUPl6xc0pKjre86iTtUQq6PtrLxOXGGL_7QivUAnMQ78EerSJGvquLgWUZocDX_tWJgIm7S0Qudc"


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
    headers = {"Authorization": f"Bearer AQDtxeBVeGXKIDjBoOetdtPmSs-sjyAPtO-T9WE-PWMZAX4vdj2YO_QE4vFeE3Ep8S2GTDsHzOce6CV4dOosThnOe6x2XMQDY_pqG4zbZQKC6F4oyw3OIMunCVtrnAS8h_vZVjzulz2XDQFdpXR0D6QRNhoKa0hbpf07Ikz5LVqhNKpv9Lj-8yCxpBjgEpFrIstkF6pdeVtVTADodnjQ9CtOXCGNNye9QXhO8OXq"}
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

if __name__ == "__main__":
    # BEARER_TOKEN = get_bearer_token()
    # Example Usage
    all_liked_songs = fetch_all_liked_songs()
    print(f"Total liked songs: {len(all_liked_songs)}")