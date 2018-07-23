# Our representation of an album, Spotify's contains far more details unnescciscary to us


class Album:
    def __init__(self, title, artist, id):
        self.title = title
        self.artist = artist
        self.id = id

    def add_to_spotify(self, sp):
        print("Adding {} by {} \n".format(self.title, self.artist))
        # sp.current_user_saved_albums_add(self.id)