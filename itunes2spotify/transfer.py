import spotipy
import spotipy.util as util
import os
import subprocess
import time
from pathlib import Path

# Transfer iTunes album that is playing to Spotify library


class Transfer:
    def __init__(self, sp, flag):
        self.flag = flag
        self.sp = sp

    # Checks if iTunes album has changed every 5 seconds, if it has add to Spotify
    def start(self):
        print("Play album in iTunes to transfer (CTRL-C to quit)")
        album = self.get_itunes_album()

        # Initial state
        changed = True
        while True:
            try:
                if changed:
                    try:
                        self.get_spotify_album(album)
                    except IndexError:
                        print("Index error")
                else:
                    time.sleep(5)
                changed, album = self.album_changed(album)
            except KeyboardInterrupt:
                return 0

    # Given an album, it is not playing in iTunes?
    def album_changed(self, album):
        new_album = self.get_itunes_album()
        if new_album and album != new_album:
            return True, new_album
        else:
            return False, album

    # Call to Swift function
    @staticmethod
    def get_itunes_album():
        file_path = Path(os.path.dirname(os.path.abspath(__file__)))
        process = subprocess.Popen(["swift", str(file_path.parent / 'res' / 'album.swift')],
                                   stdout=subprocess.PIPE)
        return str(process.communicate()[0], 'utf-8')

    # Search for album string in Spotify and add to library
    def get_spotify_album(self, it_album_str):
        results = self.sp.search(q="album:" + it_album_str, type='album')
        items = results['albums']['items'][0]
        album_id = items['uri']

        album_name = items['name']
        artist_name = items['artists'][0]['name']

        print("Found {} by {}".format(album_name, artist_name))

        # If -r mode is not set, check if correct album was found
        if self.flag:
            while True:
                ans = input("Correct? (y/n): ")
                if ans == 'y':
                    break
                elif ans == 'n':
                    return
                else:
                    ans = input("Please enter y or n: ")

        print("Adding {} by {}".format(album_name, artist_name))
        self.sp.current_user_saved_albums_add([album_id])
        print("Done")
        return
