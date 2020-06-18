class SpotifyError(Exception):
    pass

class StatusCodeError(SpotifyError):
    def __init__(self, message):
        self.message = message
