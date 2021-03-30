class SpotifyError(Exception):
    pass

class StatusCodeError(SpotifyError):
    def __init__(self, status_code):
        self.message = 'Error! API returned error code ' + status_code
