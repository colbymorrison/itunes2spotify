# Our representation of an album, Spotify's contains far more details unnescciscary to us


class Album:
    def __init__(self, title, artist, id):
        self.title = title
        self.artist = artist
        self.id = id
