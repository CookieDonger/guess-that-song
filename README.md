 # Guess That Song!
#### Link to Site: http://guessthatsong.us-east-2.elasticbeanstalk.com/
#### Description: A website which will connect to your spotify app and play random parts of your songs.

<p>
This repository contains the local version of the project, which you can download and run by downloading the necessary packages in the requirements.txt
into a venv and then starting it. Type python3 application.py in the main directory and it should open a page at 127.0.0.1:5000. This local version has
all of the same functions as the deployed version, just using a different Spotify application as the web version requires me to authenticate anyone who
wishes to use it as it is currently in development mode.
</p>

### application.py

<p>
Application.py handles all of the different routes of the project, and was renamed from app.py as to deploy it onto
AWS servers.
</p>
<p>
Within application.py, I started up Flask and imported some data from my dotenv files to keep my Spotify project information safe.
I decided to set up session variables for the random numbers which determined which song to play in order to keep variables separate
for each user.
</p>

#### /index

<p>
The index route has an error message that will appear if things go wrong, along with showing the playlists that have already
been entered. It won't allow any link that isn't to a Spotify playlist or any duplicates.
</p>

#### /delete

<p>
Delete simply removes a playlist from the list.
</p>

#### /guess

<p>
Guess takes the variables for RNG so that it can choose a random song. If the variables for RNG have not been set,
it will not play a song. If no active player is found, it will return to index will an error message saying so. If length is equal
to 0, then it shall not use the part variable when playing.
</p>

#### /reload

<p>
Reload will reroll the numbers and find a new excerpt to play, and it makes sure that the song, part, and playlist exist by using
the Spotify data, hence why I decided to only limit it to Spotify playlists because albums and tracks have different data to simplify the process of gathering data.
</p>

#### /reveal  

<p>
Reveal just takes the data of the song name and artist(Composer), and then just puts it onto the HTML for the user to see via render_template, again
this is why I only allowed playlists.
</p>

### helpers.py

<p>
helpers.py was supposed to be bigger, but when I discovered Spotipy it made my life much easier, removing the need for Javascript or
much helpers.py to deal with authentication, so it only has a lookup function to check if a site exists.
</p>

### static: styles.css

<p>
static contains my styles.css, which just gave me the style choices I made, along with the Spotify-esque buttons and the overall Spotify feel.
</p>

### templates: layout.html, index.html, guess.html, login.html

<p>
templates contains layout.html, which is what I used to create the headers of the webpage. index.html and guess.html have small differences
in their links so the user can tell which page they're on, but other than that it's just extending it off of layout.html to write less code.
</p>
