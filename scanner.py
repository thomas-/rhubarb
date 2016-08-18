from flask import Flask
import sys
import os
import fnmatch

from mutagen.mp3 import EasyMP3 as MP3

from rhubarb import db, Track, Playlist

# from hashlib import sha256

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///music.db'


def add_mp3(db, path):
    try:
        audio = MP3(path)
        path = path.replace('\\', '/')
        artist = audio['performer'][0] if 'performer' in audio else \
            audio['artist'][0] if 'artist' in audio else "Unknown artist"
        title = audio['title'][0] if 'title' in audio else "?"
        tracknumber = audio['tracknumber'][0] if audio['tracknumber'] else None
        try:
            # naively try to convert 2/12 style tracknumbers into just ints
            # not hugely important to cater for obscure formats
            tracknumber = int(tracknumber.split("/")[0])
        except:
            tracknumber = None
        album = audio['album'][0] if 'album' in audio else "Unknown album"
        genre = audio['genre'][0] if 'genre' in audio else None
        year = audio['date'][0] if 'date' in audio else None
        length = audio.info.length
        bitrate = audio.info.bitrate
        track = Track(path.decode('utf-8', 'ignore'), artist, title, tracknumber, album,
                      genre, year, length, bitrate)
        db.session.add(track)
        print "added: ", artist, title, tracknumber
    except Exception as e:
        print e


def init(db):
    db.drop_all()
    db.create_all()
    for root, dirs, files in os.walk('music'):
        for mp3 in fnmatch.filter(files, '*.mp3'):
            add_mp3(db, os.path.join(root, mp3))
    now_playing = Playlist("NOW PLAYING", -1)
    db.session.add(now_playing)
    db.session.commit()


def update(db):
    for root, dirs, files in os.walk('music'):
        for mp3 in fnmatch.filter(files, '*.mp3'):
            path = os.path.join(root, mp3)
            if db.session.query(Track.id).filter_by(path=path.decode('utf-8', 'ignore')).scalar() is None:
                add_mp3(db, path)
            else:
                print "skipping %s (already added)" % path
    db.session.commit()


def clean(db):
    tracks = Track.query.all()
    for track in tracks:
        if not os.path.isfile(track.path):
            db.session.delete(track)
            print "deleted %s - %s (file missing)" % (track.artist, track.title)
    db.session.commit()


if __name__ == '__main__':
    db.init_app(app)
    with app.app_context():
        if len(sys.argv) > 1:
            cmd = sys.argv[1]
            if cmd == "init":
                init(db)
            elif cmd == "clean":
                clean(db)
            elif cmd == "update":
                update(db)
            else:
                print "unknown command: %s" % cmd
        else:
            update(db)
