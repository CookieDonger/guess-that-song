import os
from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from helpers import lookup
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time
import random

application = Flask(__name__)

application.secret_key = b'0d498dd9a4ea4b34f02cf616f5e0d2dc1ee60ac60526a6b4ed4ed9eec5bb04f4'
application.config['SESSION_PERMANENT'] = False
application.config['SESSION_TYPE'] = 'filesystem'
application.config['SESSION_FILE_DIR'] = './.flask_session/'
Session(application)

load_dotenv()

CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
REDIRECT_URI = os.getenv('SPOTIPY_REDIRECT_URI')
scope = "user-read-playback-state user-modify-playback-state user-read-currently-playing"


@application.before_request
def before_request():
    session['error'] = ''
    return


# Should do magic cache stuff, I'm not sure myself lol
@application.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@application.route('/login', methods=['GET'])
def login():
    if request.method == 'GET':
        return render_template('login.html')


@application.route('/logout')
def logout():
    session.clear()
    return redirect('/')


@application.route("/", methods=["GET", "POST"])
def index():

    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(scope=scope, cache_handler=cache_handler, show_dialog=True)

    if request.args.get('code'):
        auth_manager.get_access_token(request.args.get('code'))
        session['playlists'] = []
        session['playlist'] = ''
        session['track'] = 0
        session['length'] = 0
        session['part'] = 0
        session['has_excerpt'] = False
        session['error'] = ''
        return redirect('/')

    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        auth_url = auth_manager.get_authorize_url()
        return render_template('login.html', url=auth_url)

    # Just setting up the index page
    if request.method == "GET":
        return render_template("index.html", playlists=session['playlists'])
    if request.method == "POST":
        url = request.form.get("url")
        session['playlistadd'] = lookup(url)
        # If the URL does not exist
        if session['playlistadd'] is None:
            session['error'] = "Invalid URL"
            return render_template("index.html", error=session['error'], playlists=session['playlists'])
        # If the URL is not a spotify playlist
        elif "open.spotify.com/playlist/" not in url:
            session['error'] = "Not a spotify playlist"
            return render_template("index.html", error=session['error'], playlists=session['playlists'])
        # Adding playlist to the list of playlists
        else:
            # Telling user if playlist already exists
            if url in session['playlists']:
                session['error'] = "Playlist has already been added"
                return render_template("index.html", error=session['error'], playlists=session['playlists'])
            else:
                session['playlists'].append(url)
                session['error'] = ''
                return render_template("index.html", error=session['error'], playlists=session['playlists'])


# Option to remove playlists
@application.route("/delete", methods=["POST"])
def delete():
    session['playlists'].remove(request.form.get("playlist"))
    return redirect("/")


# Here's where we manipulate the global variables
@application.route("/guess", methods=["GET", "POST"])
def guess():
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)

    if request.method == "GET":
        # Not letting you go to the page if you have no playlists
        if len(session['playlists']) == 0:
            return redirect("/")
        return render_template("guess.html")
    # Starting playback
    if request.method == "POST":
        # You need to get an excerpt first, so I just redirect if there is no excerpt
        if session['has_excerpt'] is False:
            return render_template('index.html', error='No excerpt yet')

        sp = spotipy.Spotify(auth_manager=auth_manager)

        # For whole song
        if session['length'] == 0:
            # Making sure there's an active device
            try:
                sp.start_playback(device_id=sp.devices()['devices'][0]['id'], context_uri=session['playlist'], offset={"position": session['track']})
            except Exception:
                session['error'] = "No active device found"
                return render_template("index.html", error=session['error'], playlists=session['playlists'])
        # For excerpts
        else:
            # Again making sure there's an active device
            try:
                sp.start_playback(device_id=sp.devices()['devices'][0]['id'], context_uri=session['playlist'], offset={"position": session['track']}, position_ms=session['part'])
                time.sleep(int(session['length']))
                sp.pause_playback()
            except Exception:
                session['error'] = "No active device found"
                return render_template("index.html", error=session['error'], playlists=session['playlists'])
        return ('', 204)


# Getting a new excerpt
@application.route("/reload", methods=["POST"])
def reload():
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)

    # Checking if user specified length
    if request.form.get("length"):
        session['length'] = int(request.form.get("length"))
    # Random playlist
    rng = random.randint(0, len(session['playlists']) - 1)
    session['playlist'] = session['playlists'][rng]

    sp = spotipy.Spotify(auth_manager=auth_manager)

    # Random track
    session['total'] = sp.playlist_items(session['playlist'], fields='total')
    session['total'] = session['total']['total']
    session['track'] = random.randint(0, session['total'] - 1)
    # Random part
    session['duration'] = sp.playlist_tracks(session['playlist'], fields='items', limit=1, offset=session['track'])
    session['duration'] = int(session['duration']['items'][0]['track']['duration_ms'])
    lengthms = int(session['length']) * 1000
    session['part'] = random.randint(0, session['duration'] - int(lengthms))
    session['has_excerpt'] = True
    return ('', 204)


# This was a pain, I had to figure out the data that Spotify gave and figure out the lists and dictionaries to get the info
# I did both song name and composer because some songs have the same name.
@application.route("/reveal", methods=["POST"])
def reveal():
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    sp = spotipy.Spotify(auth_manager=auth_manager)

    if not session['track']:
        return render_template('index.html', error='No excerpt yet')
    session['song'] = sp.playlist_tracks(session['playlist'], fields='items', limit=1, offset=session['track'])
    session['songname'] = session['song']['items'][0]['track']['name']
    session['name'] = session['song']['items'][0]['track']['artists'][0]['name']
    return render_template("guess.html", songname=session['songname'], name=session['name'])


if __name__ == "__main__":
    application.debug = True
    application.run()
