Spotify Web API in Python
=====================

Installation
------------

`pip install spotifywebapi`

Setup
-----

```
export SPOTIFY_CLIENT_ID=client_id_here
export SPOTIFY_CLIENT_SECRET=client_secret_here
```

### Client

```python
import spotifywebapi, os

sp = spotifywebapi.Spotify(os.getenv('SPOTIFY_CLIENT_ID'), os.getenv('SPOTIFY_CLIENT_SECRET'))
```

### User

```python
user = sp.getAuthUser(refreshtoken_for_user)
```