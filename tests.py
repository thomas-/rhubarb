import unittest
import sys
from base64 import b64encode
import json

from rhubarb import db, app
from models import Track, Playlist, PlaylistTracks


# filter SQLAlchemy unnecessary warnings re: Decimal objects
# http://stackoverflow.com/questions/34674029/sqlalchemy-query-raises-unnecessary-warning-about-sqlite-and-decimal-how-to-spe
import warnings
from sqlalchemy.exc import SAWarning
warnings.filterwarnings('ignore',
                        r"^Dialect sqlite\+pysqlite does \*not\* support Decimal objects natively\, "
                        "and SQLAlchemy must convert from floating point - rounding errors and other "
                        "issues may occur\. Please consider storing Decimal numbers as strings or "
                        "integers on this platform for lossless storage\.$",
                        SAWarning, r'^sqlalchemy\.sql\.type_api$')

db.init_app(app)


# define auth headers to use when requesting routes
headers = {"Authorization": "Basic {user}".format(user=b64encode(b"test:testpass"))}


class RhubarbTests(unittest.TestCase):

    def test_auth(self):
        r = self.rhubarb.get("/", headers=headers)
        self.assertEquals(r.status_code, 200)

    def test_bad_auth(self):
        # Important to ensure wrong passwords can't gain access
        r = self.rhubarb.get("/", headers={"Authorization": "Basic {user}".format(user=b64encode(b"wrong:wrong"))})
        self.assertEquals(r.status_code, 401)

    def test_search(self):
        r = self.rhubarb.get("/search?query=blood", headers=headers)
        data = json.loads(r.data)
        self.assertEquals(data['tracks'][0]['id'], 1)
        r = self.rhubarb.get("/search?query=you love", headers=headers)
        data = json.loads(r.data)
        self.assertEquals(len(data['tracks']), 4)

    def test_artists(self):
        r = self.rhubarb.get("/artists", headers=headers)
        data = json.loads(r.data)
        artists = data['artists']
        self.assertEquals(artists[0]['title'], "G-Eazy")
        self.assertEquals(artists[1]['title'], "Taylor Swift")
        self.assertEquals(artists[2]['title'], "You Love Her Coz She's Dead")

    def test_albums(self):
        r = self.rhubarb.get("/albums", headers=headers)
        data = json.loads(r.data)
        albums = data['albums']
        self.assertEquals(albums[0]['title'], "1989")
        self.assertEquals(albums[1]['title'], "Inner City Angst EP")
        self.assertEquals(albums[2]['title'], "Red")
        self.assertEquals(albums[3]['title'], "When It's Dark Out")

    def test_tracks_by_artist(self):
        r = self.rhubarb.get("/tracks?artist=G-Eazy", headers=headers)
        data = json.loads(r.data)
        tracks = data['tracks']
        self.assertEquals(len(tracks), 1)
        self.assertEquals(tracks[0]['id'], 6)

    def test_tracks_by_artist_album(self):
        r = self.rhubarb.get("/tracks?artist=Taylor Swift&album=Red", headers=headers)
        data = json.loads(r.data)
        tracks = data['tracks']
        self.assertEquals(len(tracks), 1)
        self.assertEquals(tracks[0]['id'], 7)

    def test_playlist_new(self):
        r = self.rhubarb.post('/playlist/new', headers=headers, data={"name": "Test Playlist"})
        res = json.loads(r.data)
        data = {"id": 6, "name": "Test Playlist"}
        self.assertEquals(res, data)
        playlist = Playlist.query.get(res['id'])
        self.assertEquals(playlist.name, res['name'])

    def test_playlist_delete(self):
        r = self.rhubarb.post('/playlist/delete', headers=headers, data={"id": 4})
        self.assertEquals(r.data, "OK")
        playlist = Playlist.query.get(4)
        self.assertIsNone(playlist)

    def test_playlist_sort(self):
        data = {"playlistsJSON":
                json.dumps({u'playlists': [{u'sort': 0, u'id': 5}, {u'sort': 1, u'id': 4}, {u'sort': 2, u'id': 3}, {u'sort': 3, u'id': 2}]})
                }
        r = self.rhubarb.post('/playlist/sort', headers=headers, data=data)
        self.assertEquals(r.data, "OK")
        playlist5 = Playlist.query.get(5)
        playlist2 = Playlist.query.get(2)
        self.assertEquals(playlist5.sort, 1)
        self.assertEquals(playlist2.sort, 4)

    def test_playlist_add(self):
        data = {"playlist": 5, "track": 1}
        r = self.rhubarb.post('/playlist/add', headers=headers, data=data)
        self.assertEquals(r.data, "OK")
        playlist = Playlist.query.get(5)
        pt = playlist.tracks[-1]
        self.assertEquals(pt.track.id, 1)

    def test_playlist_remove(self):
        data = {"pt": 2}
        r = self.rhubarb.post('/playlist/remove', headers=headers, data=data)
        self.assertEquals(r.data, "OK")
        pt = PlaylistTracks.query.get(2)
        self.assertIsNone(pt)
        playlist = Playlist.query.get(2)
        self.assertEquals(len(playlist.tracks), 3)

    def test_playlist_get_tracks(self):
        r = self.rhubarb.get('/playlist/tracks/2', headers=headers)
        data = json.loads(r.data)
        mock_playlist_tracks = {u'sort': 1, u'tracks': [{u'album': u'Inner City Angst EP', u'pt': 2, u'title': u'Blood Lust', u'artist': u"You Love Her Coz She's Dead", u'year': 2010, u'duration': u'4:05', u'tracknumber': 1, u'id': 1}, {u'album': u'Inner City Angst EP', u'pt': 3, u'title': u'Dead End', u'artist': u"You Love Her Coz She's Dead", u'year': 2010, u'duration': u'3:43', u'tracknumber': 2, u'id': 2}, {u'album': u'Inner City Angst EP', u'pt': 4, u'title': u'Superheroes', u'artist': u"You Love Her Coz She's Dead", u'year': 2010, u'duration': u'2:45', u'tracknumber': 3, u'id': 3}, {u'album': u'Inner City Angst EP', u'pt': 5, u'title': u'Wizards', u'artist': u"You Love Her Coz She's Dead", u'year': 2010, u'duration': u'3:25', u'tracknumber': 4, u'id': 4}], u'id': 2, u'name': u'Playlist'}
        self.assertEquals(data, mock_playlist_tracks)

    def test_playlist_post_tracks(self):
        # reverse data in in playlist 2
        data = {"tracksJSON": '{"tracks":[4,3,2,1]}'}
        r = self.rhubarb.post('/playlist/tracks/2', headers=headers, data=data)
        self.assertEquals(r.data, "OK")
        playlist = Playlist.query.get(2)
        pts = playlist.tracks
        self.assertEquals(pts[0].track.id, 4)
        self.assertEquals(pts[3].track.id, 1)

    def test_playlist_as_dict(self):
        playlist = Playlist.query.get(1)
        data = {'sort': -1, 'tracks': [{'album': u'Inner City Angst EP', 'pt': 1, 'title': u'Blood Lust', 'artist': u"You Love Her Coz She's Dead",
                'year': 2010, 'duration': '4:05', 'tracknumber': 1, 'id': 1}], 'id': 1, 'name': u'NOW PLAYING'}
        self.assertEquals(playlist.as_dict(), data)

    def test_track_as_dict(self):
        track = Track.query.get(1)
        data = {'album': u'Inner City Angst EP', 'title': u'Blood Lust', 'artist': u"You Love Her Coz She's Dead", 'year': 2010, 'duration': '4:05',
                'tracknumber': 1, 'id': 1}
        self.assertEquals(track.as_dict(), data)

    def test_track_durations(self):
        durations = [
                [1, "4:05"],
                [2, "3:43"],
                [3, "2:45"],
                [4, "3:25"]
                ]
        for id, duration in durations:
            track = Track.query.get(id)
            self.assertEqual(track.duration, duration)

    def generate_mock_data(self, db):
        tracks = [
                Track("mock", "You Love Her Coz She's Dead", "Blood Lust", "1", "Inner City Angst EP", "Dance", "2010", "245.394286", "320"),
                Track("mock", "You Love Her Coz She's Dead", "Dead End", "2", "Inner City Angst EP", "Dance", "2010", "223.608163", "320"),
                Track("mock", "You Love Her Coz She's Dead", "Superheroes", "3", "Inner City Angst EP", "Dance", "2010", "165.459592", "320"),
                Track("mock", "You Love Her Coz She's Dead", "Wizards", "4", "Inner City Angst EP", "Dance", "2010", "205.374694", "320"),
                Track("mock", "Taylor Swift", "Blank Space", "2", "1989", "Pop", "2015", "240", "320"),
                Track("mock", "G-Eazy", "Me, Myself & I", "3", "When It's Dark Out", "Rap", "2016", "210", "320"),
                Track("mock", "Taylor Swift", "22", "5", "Red", "Pop", "2013", "300", "320")
                ]
        for track in tracks:
            db.session.add(track)
        now_playing = Playlist("NOW PLAYING", -1)
        db.session.add(now_playing)
        playlists = [
                Playlist("Playlist", 1),
                Playlist("Playlist 2", 2),
                Playlist("Playlist 3", 3),
                Playlist("Playlist 4", 4)
                ]
        for playlist in playlists:
            db.session.add(playlist)
        playlist_tracks = [
                PlaylistTracks(playlist=now_playing, track=tracks[0], sort=0),
                PlaylistTracks(playlist=playlists[0], track=tracks[0], sort=1),
                PlaylistTracks(playlist=playlists[0], track=tracks[1], sort=2),
                PlaylistTracks(playlist=playlists[0], track=tracks[2], sort=3),
                PlaylistTracks(playlist=playlists[0], track=tracks[3], sort=4),
                ]
        for pt in playlist_tracks:
            db.session.add(pt)
        db.session.commit()

    def setUp(self):
        self.app = app
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tests.db'
        self.app.config['USERNAME'] = 'test'
        self.app.config['PASSWORD'] = 'testpass'
        self.rhubarb = app.test_client()
        db.app = self.app
        with self.app.app_context():
            db.create_all()
            self.generate_mock_data(db)

    def tearDown(self):
        # self.app = app
        # self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tests.db'
        # db.init_app(self.app)
        with self.app.app_context():
            db.drop_all()

if __name__ == '__main__':
    if(len(sys.argv) > 1):
        unittest.main()
    else:
        suite = unittest.TestLoader().loadTestsFromTestCase(RhubarbTests)
        unittest.TextTestRunner(verbosity=2).run(suite)
