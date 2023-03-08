import os
from flask import Flask, redirect, render_template, request
from helpers import lookup
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time
import random

app = Flask(__name__)

load_dotenv()

CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
REDIRECT_URI = os.getenv('SPOTIPY_REDIRECT_URI')

# Doing these as globals due to needing reveal and guess to both use the same variables
playlists = []
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=REDIRECT_URI, scope="user-read-playback-state user-modify-playback-state user-read-currently-playing"))
playlist = ''
track = 0
length = 0
part = 0
has_excerpt = False

# Should do magic cache stuff, I'm not sure myself lol
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET", "POST"])
def index():
    global length
    error = ""
    # Just setting up the index page
    if request.method == "GET":
        length = 0
        return render_template("index.html", error=error, playlists=playlists)
    if request.method == "POST":
        url = request.form.get("url")
        playlist = lookup(url)
        # If the URL does not exist
        if playlist is None:
            error = "Invalid URL"
            return render_template("index.html", error=error, playlists=playlists)
        # If the URL is not a spotify playlist
        elif "open.spotify.com/playlist/" not in url:
            error = "Not a spotify playlist"
            return render_template("index.html", error=error, playlists=playlists)
        # Adding playlist to the list of playlists
        else:
            # Telling user if playlist already exists
            if url in playlists:
                error = "Playlist has already been added"
                return render_template("index.html", error=error, playlists=playlists)
            else:
                playlists.append(url)
                return render_template("index.html", error=error, playlists=playlists)


# Option to remove playlists
@app.route("/delete", methods=["POST"])
def delete():
    playlist = request.form.get("playlist")
    playlists.remove(playlist)
    return redirect("/")


# Here's where we manipulate the global variables
@app.route("/guess", methods=["GET", "POST"])
def guess():
    global track
    global length
    global playlist
    global part
    if request.method == "GET":
        # Not letting you go to the page if you have no playlists
        if len(playlists) == 0:
            return redirect("/")
        return render_template("guess.html")
    # Starting playback
    if request.method == "POST":
        # You need to get an excerpt first, so I just redirect if there is no excerpt
        if has_excerpt is False:
            return redirect("/guess")
        # For whole song
        if length == 0:
            # Making sure there's an active device
            try:
                sp.start_playback(context_uri=playlist, offset={"position": track})
            except Exception:
                error = "No active device found"
                return render_template("index.html", error=error, playlists=playlists)
        # For excerpts
        else:
            # Again making sure there's an active device
            try:
                sp.start_playback(context_uri=playlist, offset={"position": track}, position_ms=part)
                time.sleep(int(length))
                sp.pause_playback()
            except Exception:
                error = "No active device found"
                return render_template("index.html", error=error, playlists=playlists)
        return redirect("/guess")


# Getting a new excerpt
@app.route("/reload", methods=["POST"])
def reload():
    global track
    global length
    global playlist
    global part
    global has_excerpt
    # Checking if user specified length
    if request.form.get("length"):
        length = int(request.form.get("length"))
    # Random playlist
    rng = random.randint(0, len(playlists) - 1)
    playlist = playlists[rng]
    # Random track
    total = sp.playlist_items(playlist, fields='total')
    total = total['total']
    track = random.randint(0, total - 1)
    # Random part
    duration = sp.playlist_tracks(playlist, fields='items', limit=1, offset=track)
    duration = int(duration['items'][0]['track']['duration_ms'])
    lengthms = int(length) * 1000
    part = random.randint(0, duration - int(lengthms))
    has_excerpt = True
    return render_template("guess.html")


# This was a pain, I had to figure out the data that Spotify gave and figure out the lists and dictionaries to get the info
# I did both song name and composer because some songs have the same name.
@app.route("/reveal", methods=["POST"])
def reveal():
    song = sp.playlist_tracks(playlist, fields='items', limit=1, offset=track)
    songname = song['items'][0]['track']['name']
    name = song['items'][0]['track']['artists'][0]['name']
    return render_template("guess.html", songname=songname, name=name)
