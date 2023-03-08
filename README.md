# Guess That Song!
#### Video Demo:  <https://youtu.be/oVMbu6hteU8>
#### Description: A website which will connect to your spotify app and play random parts of your songs.

# app.py

<p>The first file, app.py, is the main part of the project. I decided to make a webpage using
python and HTML documents for the web part of the project, so this meant that there wasn't
much Javascript, which was fine with me because I'm less experienced and less comfortable
using Javascript compared to Python.
</p>
<p>Within app.py, I started up Flask and imported some data from my dotenv files to keep my Spotify project information safe.
I decided to set up global variables for the random numbers which determined which song to play because I had multiple
routes which needed to manipulate these numbers in order to make it as easy to use for the user.
</p>

# /index

<p>The index route has an error message that will appear if things go wrong, along with showing the playlists that have already
been entered. It won't allow any link that isn't to a Spotify playlist or any duplicates.
</p>

# /delete

<p>Delete simply removes a playlist from the list.
</p>

# /guess

<p>Guess takes the global variables for RNG so that it can choose a random song. If the global variables for RNG have not been set,
it will not play a song. If no active player is found, it will return to index will an error message saying so. If length is equal
to 0, then it shall not use the part global variable when playing.
</p>

# /reload

<p>Reload will reroll the numbers and find a new excerpt to play, and it makes sure that the song, part, and playlist exist by using
the Spotify data, hence why I decided to only limit it to Spotify playlists because albums and tracks have different data and that was
painful to try and figure out how to access the data.
</p>

# /reveal

<p>Reveal just takes the data of the song name and artist(Composer), and then just slaps it onto the HTML for the user to see, again
this is why I only allowed playlists.
</p>

# helpers.py

<p>helpers.py was supposed to be bigger, but when I discovered Spotipy it made my life much easier, removing the need for Javascript or
much helpers.py to deal with authentication, so it only has a lookup function to check if a site exists.
</p>

# static, styles.css

<p>static contains my styles.css, which just gave me the style choices I made, along with the Spotify-esque buttons
</p>

# templates, .html

<p>templates contains layout.html, which is what I used to create the headers of the webpage. index.html and guess.html have small differences
in their links so the user can tell which page they're on, but other than that it's just extending it off of layout.html to write less code.
</p>

# venv

<p>venv had my virtual environment which was quite the experience to figure out and get working, and even now I'm not sure why some things
don't work, but I guess that's how it goes sometimes.
</p>
