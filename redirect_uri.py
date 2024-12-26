import requests
from flask import Flask, request, jsonify
import webbrowser
from pymongo import MongoClient

# Replace with your Spotify app credentials
CLIENT_ID = "e91218f06acf4549b91aa7053c8d1b8b"
CLIENT_SECRET = "3c4485af7c4b4413918417704b5ca634"
REDIRECT_URI = "http://localhost:8888/callback"

# Flask App Initialization
app = Flask(__name__)

# Global variable to store the access token
access_token = None

@app.route('/')
def index():
    # Generate the Spotify authorization URL
    auth_url = (
        f"https://accounts.spotify.com/authorize"
        f"?client_id={CLIENT_ID}"
        f"&response_type=code"
        f"&redirect_uri={REDIRECT_URI}"
        f"&scope=user-library-read"
    )
    return f'<h1>Authorize</h1><p><a href="{auth_url}">Click here to authorize Spotify access</a></p>'

@app.route('/callback', methods=['GET'])
def spotify_callback():
    global access_token
    error = request.args.get('error')
    code = request.args.get('code')
    
    if error:
        return jsonify({"status": "error", "message": error}), 400
    
    if code:
        # Exchange authorization code for access token
        token_url = "https://accounts.spotify.com/api/token"
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT_URI,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET
        }
        response = requests.post(token_url, data=data)
        
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data["access_token"]
            
            # Fetch all liked songs immediately after authorization
            liked_songs = fetch_all_liked_songs()  # Fetch all songs
            if liked_songs:
                # Add songs to MongoDB
                insert_tracks_to_mongo("liked_songs", liked_songs)  # Change "Liked Songs" to your playlist name
                
                # Display the liked songs in the browser
                song_list = "<ul>"
                for song in liked_songs:
                    song_list += f"<li>{song['name']} by {song['artist']} (Album: {song['album']})</li>"
                song_list += "</ul>"
                return f"<h1>Authorization successful!</h1><h2>Your Liked Songs:</h2>{song_list}"
            else:
                return "<h1>Authorization successful!</h1><p>Could not fetch liked songs.</p>"
        else:
            return jsonify({"status": "error", "message": response.json()}), response.status_code
    
    return jsonify({"status": "error", "message": "Missing parameters"}), 400

def fetch_all_liked_songs():
    if not access_token:
        print("Error: Access token not available.")
        return []
    
    all_tracks = []
    url = "https://api.spotify.com/v1/me/tracks"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    params = {
        "limit": 50,  # Fetch 50 songs per request (max allowed by Spotify)
        "offset": 0
    }
    
    while url:
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code != 200:
            print(f"Error: {response.status_code}, {response.json()}")
            return []
        
        data = response.json()
        for item in data['items']:
            track = item['track']
            all_tracks.append({
                "name": track['name'],
                "artist": ", ".join(artist['name'] for artist in track['artists']),
                "album": track['album']['name'],
                "id": track['id'],
                "uri": track['uri']
            })
        
        # If there's another page, use the "next" URL for pagination
        url = data.get('next')
        if url:
            params = {}  # Don't need additional params if "next" URL is provided
    
    return all_tracks

def insert_tracks_to_mongo(playlist_name, tracks):
    # MongoDB Setup (change URI as needed)
    mgc = MongoClient()
    db = mgc["music_madness"]  # Use your desired database name
    
    # Get or create the collection for the given playlist name
    collection = db[playlist_name]
    
    # Insert the tracks into the collection
    if tracks:
        result = collection.insert_many(tracks)
        print(f"Inserted {len(result.inserted_ids)} tracks into '{playlist_name}' collection.")
    else:
        print(f"No tracks to insert into '{playlist_name}' collection.")

if __name__ == '__main__':
    # Open authorization page in default browser
    webbrowser.open(f"http://localhost:8888/")
    # Start the Flask server
    app.run(host='localhost', port=8888)
