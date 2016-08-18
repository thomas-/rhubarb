import os
import json
from functools import wraps
from flask import Flask, Response, render_template, request, jsonify

from lib.http import send_file_partial

from models import db, Track, Playlist, PlaylistTracks

app = Flask(__name__)
app.config.from_pyfile('config.py')


def login(username, password):
    # ensure credentials are correct
    return username == app.config['USERNAME'] and password == app.config['PASSWORD']


def auth(f):
    # wrapper to force authentication on wrapped routes
    # we dont want pirates or user data leaking
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not login(auth.username, auth.password):
            return Response("Login required", 401, {"WWW-Authenticate": 'Basic realm="Login Required"'})
        return f(*args, **kwargs)
    return decorated


@app.route('/')
@auth
def index():
    # serve the front-end app with some initially rendered data
    playlist = Playlist.query.get(1)
    tracks = [pt.as_dict() for pt in playlist.tracks]
    artists = db.session.query(Track.artist).order_by(db.func.lower(Track.artist)).distinct()
    albums = db.session.query(Track.album, Track.artist).order_by(Track.album).distinct()
    artists = [{"title": artist[0]} for artist in artists]
    albums = [{"title": album[0], "artist": album[1]} for album in albums]
    playlists = Playlist.query.filter(Playlist.sort >= 0).order_by(Playlist.sort).all()
    return render_template('index.html', artists=artists, albums=albums, tracks=tracks, playlists=playlists)


@app.route('/music/<path:path>')
@auth
def send_music(path):
    return send_file_partial(os.path.join(path))


@app.route('/music/track/<int:id>')
@auth
def send_track(id):
    track = Track.query.get(id)
    return send_file_partial(os.path.join(track.path))


@app.route('/artists')
@auth
def artists():
    artists = db.session.query(Track.artist).order_by(db.func.lower(Track.artist)).distinct()
    artists = [{"title": artist[0]} for artist in artists]
    return jsonify({"artists": artists})


@app.route('/albums')
@auth
def albums():
    albums = db.session.query(Track.album, Track.artist).order_by(Track.album).distinct()
    albums = [{"title": album[0], "artist": album[1]} for album in albums]
    return jsonify({"albums": albums})


@app.route('/tracks')
@auth
def send_results():
    artist = request.args.get('artist')
    album = request.args.get('album')
    tracks = Track.query
    if album and artist:
        tracks = tracks.filter_by(artist=artist, album=album)
    elif artist:
        tracks = tracks.filter_by(artist=artist)
    tracks = tracks.order_by(db.func.lower(Track.artist), Track.album, Track.tracknumber).all()
    tracks = [track.as_dict() for track in tracks]
    return jsonify({"tracks": tracks})


@app.route('/search')
@auth
def search():
    query = request.args.get('query')
    tracks = Track.query
    # search artist + album + title fields, match any
    tracks = tracks.filter(db.or_(Track.artist.contains(query), Track.album.contains(query), Track.title.contains(query)))
    tracks = tracks.all()
    tracks = [track.as_dict() for track in tracks]
    return jsonify({"tracks": tracks})


@app.route('/playlist/new', methods=['POST'])
@auth
def new_playlist():
    name = request.form['name']
    playlist = Playlist(name, 0)
    db.session.add(playlist)
    db.session.commit()
    return jsonify({"id": playlist.id, "name": playlist.name})


@app.route('/playlist/sort', methods=['POST'])
@auth
def sort_playlists():
    data = json.loads(request.form['playlistsJSON'])
    for item in data["playlists"]:
        playlist = Playlist.query.get(item['id'])
        playlist.sort = int(item['sort']) + 1
    db.session.commit()
    return "OK"


@app.route('/playlist/add', methods=['POST'])
@auth
def add_to_playlist():
    playlist_id = int(request.form['playlist'])
    track_id = int(request.form['track'])
    playlist = Playlist.query.get(playlist_id)
    track = Track.query.get(track_id)
    # specify large sort number to ensure track is added to the bottom
    # of the playlist
    playlist_track = PlaylistTracks(playlist=playlist, track=track, sort=99999)
    db.session.add(playlist_track)
    db.session.commit()
    return "OK"


@app.route('/playlist/tracks/<int:id>', methods=['GET', 'POST'])
@auth
def playlist_tracks(id):
    playlist = Playlist.query.get(id)
    if request.method == 'POST':
        data = json.loads(request.form['tracksJSON'])
        playlist_tracks = playlist.tracks
        for pt in playlist_tracks:
            db.session.delete(pt)
        for sort, trackid in enumerate(data["tracks"]):
            track = Track.query.get(trackid)
            pt = PlaylistTracks(playlist=playlist, track=track, sort=sort)
            db.session.add(pt)
        db.session.commit()
        return "OK"
    else:
        return jsonify(playlist.as_dict())


@app.route('/playlist/remove', methods=['POST'])
@auth
def remove_track():
    ptid = int(request.form['pt'])
    playlist_track = PlaylistTracks.query.get(ptid)
    db.session.delete(playlist_track)
    db.session.commit()
    return "OK"


@app.route('/playlist/delete', methods=['POST'])
@auth
def delete_playlist():
    playlist_id = int(request.form['id'])
    playlist = Playlist.query.get(playlist_id)
    db.session.delete(playlist)
    db.session.commit()
    return "OK"


if __name__ == '__main__':
    db.init_app(app)
    app.run('0.0.0.0', 8080, threaded=True)
