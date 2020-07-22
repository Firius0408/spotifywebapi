import requests
import json
import time

from .exceptions import StatusCodeError, SpotifyError
from .user import User

class Spotify:

    baseurl = 'https://api.spotify.com/v1'

    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        url = 'https://accounts.spotify.com/api/token'
        payload = {
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': client_secret
            }
        r = requests.post(url, data=payload)
        if (r.status_code == 200):
            self.accessToken = r.json()['access_token']
            self.headers = {'Authorization': 'Bearer ' + self.accessToken}
        else:
            raise SpotifyError('Error! Could not successfully obtain access token with these credentials')

    def refreshAccessToken(self):
        self.__init__(self.client_id, self.client_secret)

    def getUser(self, userid):
        userid = userid.replace('spotify:user:', '')
        url = self.baseurl + '/users/' + userid
        r = requests.get(url, headers=self.headers)
        if r.status_code == 200:
            return r.json()
        else:
            raise SpotifyError('Error! Could not retrieve user for ' + userid)

    def getUserPlaylists(self, user):
        userid = user['id']
        if userid is None:
            raise SpotifyError('Error! Could not determine user id from user')

        playlists = []
        url = self.baseurl + '/users/' + userid + '/playlists?limit=50'
        while True:
            r = requests.get(url, headers=self.headers)
            status_code = r.status_code
            if status_code != 200:
                if status_code == 429:
                    time.sleep(float(r.headers['Retry-After']))
                    continue

                raise StatusCodeError('Error! API returned error code ' + str(status_code))

            playlists.extend(r.json()['items'])
            url = r.json()['next']
            if url is None:
                return playlists

    def getAuthUser(self, refreshToken):
        url = 'https://accounts.spotify.com/api/token'
        payload = {
                'grant_type': 'refresh_token',
                'refresh_token': refreshToken,
                'client_id': self.client_id,
                'client_secret': self.client_secret
                }
        r = requests.post(url, data=payload)
        if (r.status_code == 200):
            return User(self, refreshToken, r.json()['access_token'])
        else:
            raise SpotifyError('Error! Could not authenticate user with refresh token')

    def getPlaylistFromId(self, playlist):
        playlistid = playlist.replace('spotify:playlist:', '')
        url = self.baseurl + '/playlists/' + playlistid
        r = requests.get(url, headers=self.headers)
        if r.status_code == 200:
            return r.json()
        else:
            raise SpotifyError('Error! Could not retrieve playlist from ' + playlist)

    def getTracksFromItem(self, item):
        try:
            url = item['tracks']['href']
        except TypeError:
            raise SpotifyError('Error! Not a valid item')

        if url is None:
            raise SpotifyError('Error! Could not find url')

        tracks = []
        while True:
            r = requests.get(url, headers=self.headers)
            status_code = r.status_code
            if status_code != 200:
                if status_code == 429:
                    time.sleep(float(r.headers['Retry-After']))
                    continue

                raise StatusCodeError('Error! API returned error code ' + str(status_code))

            tracks.extend(r.json()['items'])
            url = r.json()['next']
            if url is None:
                return tracks

    def getItemsFromIds(self, ids, typee):
        url = self.baseurl + '/' + typee + '?ids='
        results = []
        count = 50
        if typee == 'albums': count = 20
        i = 0
        while i < len(ids):
            try:
                tempurl = url + ','.join(ids[i:i + count])
            except TypeError as err:
                raise SpotifyError(err.__str__)

            r = requests.get(tempurl, headers=self.headers)
            status_code = r.status_code
            if status_code != 200:
                if status_code == 429:
                    time.sleep(float(r.headers['Retry-After']))
                    continue

                raise StatusCodeError('Error! API returned error code ' + str(status_code))

            results.extend(r.json()[typee])
            i += count 

        return results

    def getTracksFromIds(self, trackids):
        return self.getItemsFromIds(trackids, 'tracks')

    def getAlbumsFromIds(self, albumids):
        return self.getItemsFromIds(albumids, 'albums')

    def getArtistsFromIds(self, artistids):
        return self.getItemsFromIds(artistids, 'artists')

    def search(self, string, *searchtype, limit=20):
        string = string.replace(' ', '%20')
        url = self.baseurl + '/search?q=' + string + '&type=' + ','.join(searchtype) + '&limit=' + str(limit)
        r = requests.get(url, headers=self.headers)
        status_code = r.status_code
        if status_code != 200:
            raise StatusCodeError('Error! API returned error code ' + str(status_code))
        
        return r.json()

    def getAudioFeatures(self, trackids):
        url = self.baseurl + '/audio-features?ids='
        results = []
        i = 0
        while i < len(trackids):
            tempurl = url + ','.join(trackids[i:i + 100])
            r = requests.get(tempurl, headers=self.headers)
            status_code = r.status_code
            if status_code != 200:
                if status_code == 429:
                    time.sleep(float(r.headers['Retry-After']))
                    continue

                raise StatusCodeError('Error! API returned error code ' + str(status_code))

            results.extend(r.json()['audio_features'])
            i += 100

        return results

    def getAudioAnalysis(self, trackid):
        url = self.baseurl + '/audio-analysis/' + trackid
        r = requests.get(url, headers=self.headers)
        status_code = r.status_code
        if status_code != 200:
            raise StatusCodeError('Error! API returned error code ' + str(status_code))
        
        return r.json()
