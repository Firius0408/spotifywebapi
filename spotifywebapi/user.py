import requests
import json
import datetime

from .exceptions import StatusCodeError, Error

class User:

    baseurl = 'https://api.spotify.com/v1'

    def __init__(self, client, refreshToken, accessToken):
        self.client = client
        self.refreshToken = refreshToken
        self.accessToken = accessToken
        self.headers = {'Authorization': 'Bearer ' + accessToken}
        self.contentHeaders = self.headers
        self.contentHeaders['Content-Type'] = 'application/json'
        url = self.baseurl + '/me'
        r = requests.get(url, headers=self.headers)
        if r.status_code == 200:
            self.user = r.json()
        else:
            raise Error('Error! Could not retrieve user data')

    def getClient(self):
        return self.client

    def getUser(self):
        return self.user

    def getPlaylists(self):
        try:
            return self.playlists
        except AttributeError:
            self.playlists = self.client.getUserPlaylists(self.user)
            return self.playlists

    def createPlaylist(self, name, public=True, collaborative=False, description=''):
        url = self.baseurl + '/users/' + self.user['id'] + '/playlists'
        payload = json.dumps({
            'name': name,
            'public': public,
            'collaborative': collaborative,
            'description': description
            })
        r = requests.post(url, headers=self.contentHeaders, data=payload)
        status_code = r.status_code
        if status_code != 200 and status_code != 201:
            raise StatusCodeError("Error! API returned error code " + str(status_code))

        return r.json()

    def getTop(self, term, typee, limit=20):
        url = self.baseurl + '/me/top/' + typee + '?limit=' + str(limit) + '&time_range=' + term
        r = requests.get(url, headers=self.headers)
        if r.status_code == 200:
            return r.json()
        else:
            raise Error("Error! Could not retrieve top %s for %s" % (typee, self.user['display_name']))

    def getTopArtists(self, term, limit=20):
        return self.getTop(term, 'artists', limit)

    def getTopSongs(self, term, limit=20):
        return self.getTop(term, 'tracks', limit)
