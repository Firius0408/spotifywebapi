import requests
import json

from .exceptions import StatusCodeError, SpotifyError

class User:

    baseurl = 'https://api.spotify.com/v1'
    session = requests.Session()

    def __init__(self, client: 'Spotify', refreshToken: str, accessToken: str):
        self.client = client
        self.refreshToken = refreshToken
        self.accessToken = accessToken
        self.session.headers.update({'Authorization': 'Bearer ' + accessToken})
        self.contentHeaders = {'Content-Type': 'application/json'}
        url = self.baseurl + '/me'
        r = self.session.get(url)
        if r.status_code == 200:
            self.user = r.json()
        else:
            raise SpotifyError('Error! Could not retrieve user data')

    def getClient(self) -> 'Spotify':
        return self.client

    def getUser(self) -> dict:
        return self.user

    def getPlaylists(self) -> list[dict]:
        try:
            return self.playlists
        except AttributeError:
            return self.refreshPlaylists()
        
    def refreshPlaylists(self) -> list[dict]:
        self.playlists = self.client.getUserPlaylists(self.user)
        return self.playlists

    def createPlaylist(self, name: str, public: bool = None, collaborative: bool = None, description: str = None) -> dict:
        url = self.baseurl + '/users/' + self.user['id'] + '/playlists'
        data = {
            'name': name,
            'public': public,
            'collaborative': collaborative,
            'description': description
            }
        payload = json.dumps({k: v for k, v in data.items() if v is not None})
        r = self.session.post(url, headers=self.contentHeaders, data=payload)
        status_code = r.status_code
        if status_code != 200 and status_code != 201:
            raise StatusCodeError(str(status_code))

        return r.json()
    
    def changePlaylistDetails(self, playlistid: str, name: str = None, public: bool = None, collaborative: bool = None, description: str = None) -> None:
        url = self.baseurl + '/playlists/' + playlistid
        data = {
            'name': name,
            'public': public,
            'collaborative': collaborative,
            'description': description
            }
        payload = json.dumps({k: v for k, v in data.items() if v is not None})
        r = self.session.put(url, headers=self.contentHeaders, data=payload)
        status_code = r.status_code
        if status_code != 200:
            raise StatusCodeError(str(status_code))

    def addSongsToPlaylist(self, playlistid: str, uris: list[str]) -> None:
        url = self.baseurl + '/playlists/' + playlistid + '/tracks?uris='
        for i in range(0, len(uris), 100):
            tempurl = url + ','.join(uris[i:i+100])
            r = self.session.post(tempurl)
            status_code = r.status_code
            if status_code != 201:
                raise StatusCodeError(str(status_code))

    def removeSongsFromPlaylist(self, playlistid: str, uris: list[str]) -> None:
        url = self.baseurl + '/playlists/' + playlistid + '/tracks'
        for i in range(0, len(uris), 100):
            tracks = {'tracks': [{'uri': j} for j in uris[i:i+100]]}
            r = self.session.delete(url, headers=self.contentHeaders, data=json.dumps(tracks))
            status_code = r.status_code
            if status_code != 200:
                raise StatusCodeError(str(status_code))

    def replacePlaylistItems(self, playlistid: str, uris: list[str]) -> None:
        if len(uris) > 100:
            raise SpotifyError("Error! Too many uris. Max of 100")

        url = self.baseurl + '/playlists/' + playlistid + '/tracks?uris=' + ','.join(uris)
        r = self.session.put(url)
        status_code = r.status_code
        if status_code != 201:
            raise StatusCodeError(str(status_code))

    def getTop(self, term: str, typee: str, limit: int = 20) -> dict:
        url = self.baseurl + '/me/top/' + typee + '?limit=' + str(limit) + '&time_range=' + term
        r = self.session.get(url)
        if r.status_code == 200:
            return r.json()
        else:
            raise SpotifyError("Error! Could not retrieve top %s for %s" % (typee, self.user['display_name']))

    def getTopArtists(self, term: str, limit: int = 20) -> dict:
        return self.getTop(term, 'artists', limit)

    def getTopSongs(self, term: str, limit: int = 20) -> dict:
        return self.getTop(term, 'tracks', limit)

    def followPlaylist(self, playlistid: str, public: bool = True) -> None:
        url = self.baseurl + '/playlists/' + playlistid + '/followers'
        r = self.session.put(url, headers=self.contentHeaders, data=json.dumps({'public': public}))
        status_code = r.status_code
        if status_code != 200:
            raise StatusCodeError(str(status_code))

    def unfollowPlaylist(self, playlistid: str) -> None:
        url = self.baseurl + '/playlists/' + playlistid + '/followers'
        r = self.session.delete(url)
        status_code = r.status_code
        if status_code != 200:
            raise StatusCodeError(str(status_code))