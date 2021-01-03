
# rhubarb - A Music Streaming Web-app

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

Rhubarb runs on your server or local machine, and allows playback of music
through a media player interface via the browser.


## Setup:

Rhubarb requires a few external python packages to run,

These are Flask, Flask-SQLAlchemy and Mutagen (and their dependencies)
which can either be installed manually, or using pip:

    pip install -r requirements.txt

With the dependencies installed, config.py should be edited
to specify a username, password, and to optionally change the 
default configuration options such as location of the database

Music needs to be stored as MP3 in the music/ directory

Before running rhubarb for the first time, you should populate the database
using the scanner. You can do this by running:

    python scanner.py init

To update the database at a later date, eg, to add new files and have them
be added to the database run:

    python scanner.py update

For the inverse, to clean tracks that are in the database but no longer in
the filesystem run:

    python scanner.py clean

## Running:

The application can be run by executing:

    python rhubarb.py

This will launch the server on port 8080, visit http://localhost:8080 in a browser
or the address of the server that you are hosting rhubarb on.

## Tests:

The test suite can be run by executing:

    python tests.py
    
## Screenshots:

![Now playing](http://i.imgur.com/fsPYfrH.png "Now playing")

![Library](http://i.imgur.com/CfnGQCd.png "Library view")


## API quick reference:

Below is a short reference of available API calls. At present, to see sample calls and responses it is best to consult to `tests.py`

### **Artists**
  Retrieve a list of all artists as JSON.

* **URL**

  /artists

* **Method:**

  `GET`
  
*  **URL Params**

    None

* **Data Params**

    None

### **Albums**
  Retrieve a list of all albums as JSON.

* **URL**

  /albums

* **Method:**

  `GET`
  
*  **URL Params**

    None

* **Data Params**

    None

### **Tracks**
  Accepts two parameters, artist and album, if album
is not specified then a list of all the tracks by the
artist are returned as JSON

* **URL**

  /tracks

* **Method:**

  `GET`
  
*  **URL Params**

    None

* **Data Params**

  **Required:**
  
  `artist=[string]`
  
  **Optional:**
  
  `album=[string]`

### **Search**
  Accepts a parameter query, and searches artist
name, album titles and song titles in the database
returning any matches as JSON

* **URL**

  /search

* **Method:**

  `GET`
  
*  **URL Params**

    None

* **Data Params**

  **Required:**
  
  `query=[string]`

### **New playlist**
  Accepts a parameter name, the name of the playlist to
be created. Returns the id and name of the created
playlist as JSON

* **URL**

  /playlist/new

* **Method:**

  `POST`
  
*  **URL Params**

    None

* **Data Params**

  **Required:**
  
  `name=[string]`

### **Sort playlists**
  Accepts a parameter playlistsJSON, a JSON encoded list dictionary with a playlists property that
contains a list of dictionaries with a id and sort parameter. Used to change the display order of playlists

* **URL**

  /playlist/sort

* **Method:**

  `POST`
  
*  **URL Params**

    None

* **Data Params**

  **Required:**
  
  `playlistsJSON=[Dictionary]`
  
  Dictionary in form of:
  
  `{"playlistsJSON": "playlists": [{"sort": [integer], "id": [integer]}, ...]}}`

### **Delete playlist**
  Accepts a parameter, id, a playlist id. Used to delete
a playlist from the database.

* **URL**

  /playlist/delete

* **Method:**

  `POST`
  
*  **URL Params**

    None

* **Data Params**

  **Required:**
  
  `id=[integer]`
  
### **Add track to playlist**
  Accepts two parameters, playlist (a playlist id)
and track (a track id), and adds track to the bottom of playlist

* **URL**

  /playlist/add

* **Method:**

  `POST`
  
*  **URL Params**

    None

* **Data Params**

  **Required:**
  
  `playlist=[integer]`
  
  `track=[integer]`
  
### **Retrieve playlist information/tracks**
  Retrieve the tracks and playlist metadata for the
specified playlist id as JSON

* **URL**

  /playlist/tracks/:id

* **Method:**

  `GET`
  
*  **URL Params**

  `id=[integer]`

* **Data Params**

    None
    
### **Modify playlist tracks (or change order)**
  Accepts a parameter, tracksJSON, a JSON encoded
dictionary with a tracks property that contains a
list of track id’s. Used to change the sort order of
tracks in a playlist

* **URL**

  /playlist/tracks/:id

* **Method:**

  `POST`
  
*  **URL Params**

  `id=[integer]`

* **Data Params**

  `tracksJSON=[Dictionary]`
  
  Dictionary in form of:
  
  `{"tracksJSON": '{"tracks": [4,1,3,2]}'}`
  
### **Remove a single track from a playlist**
  Accepts a parameter, pt, the playlist track id of a
track in a playlist. Removes track from playlist

* **URL**

  /playlist/remove

* **Method:**

  `POST`
  
*  **URL Params**

    None

* **Data Params**

  `pt=[integer]`
  
