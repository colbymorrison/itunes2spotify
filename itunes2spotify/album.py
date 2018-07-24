# Our representation of an album, Spotify's contains far more details unnecessary to us


class Album:
    def __init__(self, title, artist, album_id):
        self.title = title
        self.artist = artist
        self.id = album_id

    @classmethod
    def from_spfy_album(cls, spfy_album):
        return cls(spfy_album['name'], spfy_album['artists'][0]['name'], spfy_album['id'])

    def album_by_artist(self):
        return "{} by {}".format(self.title, self.artist)

    def add_to_spotify(self, sp):
        print("\nAdding {} by {} \n".format(self.title, self.artist))
        sp.current_user_saved_albums_add([self.id])