class Error(Exception):
    pass

class StatusCodeError(Error):
    def __init__(self, message):
        self.message = message
