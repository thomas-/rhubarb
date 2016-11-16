
rhubarb - A Music Streaming Web-app 
==============================================================

Rhubarb runs on your server or local machine, and allows playback of music
through a media player interface via the browser.



Setup: 
------

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

Running:
--------

The application can be run by executing

    python rhubarb.py

This will launch the server on port 8080, visit http://localhost:8080 in a browser
or the address of the server that you are hosting rhubarb on.

Tests:
------

The test suite can be run by executing

    python tests.py
    
Screenshots:
------------

![Now playing](http://i.imgur.com/fsPYfrH.png "Now playing")

![Library](http://i.imgur.com/CfnGQCd.png "Library view")
