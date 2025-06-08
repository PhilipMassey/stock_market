import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Load environment variables
#SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
#SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
SPOTIFY_CLIENT_ID='93091588579a42c3a084c5a2f983957a'
SPOTIFY_CLIENT_SECRET='114596f13e1d4bac8b680f92ea884a70'

SPOTIFY_REDIRECT_URI = 'http://localhost:8502/callback'  # or any other redirect URI you set in your app

# Authenticate with Spotify
scope = 'playlist-modify-private'
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIFY_CLIENT_ID,
                                               client_secret=SPOTIFY_CLIENT_SECRET,
                                               redirect_uri=SPOTIFY_REDIRECT_URI,
                                               scope=scope))

# Create a playlist
user_id = sp.current_user()['id']
playlist = sp.user_playlist_create(user_id, "Sunday Vibe", public=False)

# List of songs to add
songs = [
    "Come As You Are,Crowder",
"Who You Say I Am,Hillsong Worship",
"Reckless Love,Cory Asbury",
"Broken Vessels (Amazing Grace),Hillsong Worship",
"No Longer Slaves,Bethel Music",
"We Are One in the Spirit,Peter Scholtes",
"Build Your Kingdom Here,Rend Collective Oceans (Where Feet May Fail),Hillsong United",
"Bind Us Together,Bob Gillman",
"Let Us Break Bread Together,Traditional",
"10,000 Reasons (Bless the Lord),Matt Redman",
"This Is Amazing Grace,Phil Wickham",
"How Great Is Our God,Chris Tomlin",
"Trading My Sorrows,Darrell Evans",
"Happy Day,Tim Hughes",
"Amazing Grace (My Chains Are Gone),Chris Tomlin",
"Be Thou My Vision,Shane & Shane",
"Great Is Thy Faithfulness,One Sonic Society",
"It Is Well with My Soul,Shane & Shane",
"In Christ Alone,Keith Getty & Stuart Townend",
"God of Justice,Tim Hughes",
"Your Love Never Fails,Jesus Culture",
"Do Something,Matthew West",
"Chain Breaker,Zach Williams",
"All Are Welcome,Marty Haugen",
"Siyahamba (We Are Marching),Traditional",
"Here I Am to Worship,Tim Hughes",
"Blessed Be Your Name,Matt Redman",
"Jesus, We Enthrone You,Paul Kyle",
"Let the River Flow,Darrell Evans"]

# Search and add songs to the playlist
track_ids = []
for song in songs:
    song_name, artist_name = song.split(',')
    results = sp.search(q=f'track:{song_name} artist:{artist_name}', type='track')
    tracks = results['tracks']['items']
    if tracks:
        track_ids.append(tracks[0]['id'])

# Add tracks to the playlist
if track_ids:
    sp.playlist_add_items(playlist['id'], track_ids)
    print("Songs added to the playlist!")
else:
    print("No songs found to add.")