# from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Track(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.String(500), index=True)
    artist = db.Column(db.String(200))
    title = db.Column(db.String(200))
    tracknumber = db.Column(db.Integer)
    album = db.Column(db.String(200))
    genre = db.Column(db.String(200))
    year = db.Column(db.Integer)
    length = db.Column(db.Numeric)
    bitrate = db.Column(db.Integer)

    def __init__(self, path, artist, title, tracknumber, album, genre, year, length, bitrate):
        self.path = path
        self.artist = artist
        self.title = title
        self.tracknumber = tracknumber
        self.album = album
        self.genre = genre
        self.year = year
        self.length = length
        self.bitrate = bitrate

    def as_dict(self):
        return {"id": self.id,
                "artist": self.artist,
                "title": self.title,
                "tracknumber": self.tracknumber,
                "album": self.album,
                "year": self.year,
                "duration": self.duration}

    @property
    def duration(self):
        m, s = divmod(self.length, 60)
        return "%d:%02d" % (m, s)

    def __repr__(self):
        return '<Track %r - %r>' % (self.artist, self.title)


class Playlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), index=True)
    sort = db.Column(db.Integer)
    tracks = db.relationship('PlaylistTracks')

    def __init__(self, name, sort):
        self.name = name
        self.sort = sort

    def as_dict(self):
        tracks = [track.as_dict() for track in self.tracks]
        return {"id": self.id,
                "name": self.name,
                "sort": self.sort,
                "tracks": tracks}


class PlaylistTracks(db.Model):
    __tablename__ = "playlist_tracks"
    id = db.Column(db.Integer, primary_key=True)
    playlist_id = db.Column(db.Integer, db.ForeignKey('playlist.id'))
    track_id = db.Column(db.Integer, db.ForeignKey('track.id'))
    sort = db.Column(db.Integer)
    playlist = db.relationship(Playlist)
    track = db.relationship(Track)

    def as_dict(self):
        track = self.track.as_dict()
        track['pt'] = self.id
        return track

    def __repr__(self):
        return '<pt id %r, track id %r in playlist %r>' % (self.id, self.track_id, self.playlist_id)


if __name__ == '__main__':
    pass
