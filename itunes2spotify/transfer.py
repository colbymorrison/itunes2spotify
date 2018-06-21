from spotipy import SpotifyException
import spotipy.util as util
import os
import subprocess
import time
import logging
from pathlib import Path


# Transfer iTunes album that is playing to Spotify library

file_path = Path(os.path.dirname(os.path.abspath(__file__)))
logs_path = file_path.parent / 'logs.log'


class Transfer:

    def __init__(self, sp, flag):
        self.flag = flag
        self.sp = sp

        log_form = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        logging.basicConfig(file=logs_path, format=log_form, level=logging.DEBUG)
        logger = logging.getLogger()
        logger.debug("Start")
        self.logger = logging.getLogger(__name__)

    # Checks if iTunes album has changed every 5 seconds, if it has add to Spotify
    def start(self):
        print("Play album in iTunes to transfer (CTRL-C to quit)")
        logging.info("Entry msg")
        album_artist = self.get_itunes_album()
        logging.debug("Album artist {}".format(album_artist))

        # Initial state
        changed = True
        while True:
            try:
                if changed:
                    try:
                        self.get_spotify_album(album_artist[0])
                    except IndexError:
                        print("Couldn't find an album with this title in Spotify")
                    except SpotifyException:
                        self.logger.error("Soptify error")
                        print("Soptify error. Please try log in again and retry")
                else:
                    time.sleep(1)
                changed, album_artist = self.album_changed(album_artist)
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
        process = subprocess.Popen(["swift", str(file_path / 'resources' / 'album.swift')],
                                   stdout=subprocess.PIPE)
        return str(process.communicate()[0], 'utf-8').split('<')

    # Search for album string in Spotify and add to library
    def get_spotify_album(self, it_album_str):
        results = self.sp.search(q="album:" + it_album_str, type='album')
        items = results['albums']['items'][0]
        album_id = items['uri']

        album_name = items['name']
        artist_name = items['artists'][0]['name']

        # If -r mode is not set, check if correct album was found
        if self.flag:
            while True:
                album_artist = "{} by {}".format(album_name, artist_name) 
                print("Found {}".format(album_artist))
                ans = input("Correct? (y/n): ")
                if ans == 'y':
                    break
                elif ans == 'n':
                    with open('wrong_guesses', 'a+') as f:
                        f.write(album_artist)
                    self.search_artist()
                    return
                else:
                    ans = input("Please enter y or n: ")

        print("Adding {} by {} \n".format(album_name, artist_name))
        self.sp.current_user_saved_albums_add([album_id])
        return

    def search_artist(self):
        artist = self.get_itunes_album()[1]
        logging.debug("Artist: {}".format(artist))
        results = self.sp.search(q=artist, type='artist')

        id = results['artists']['items'][0]['id']
        albums = self.sp.artist_albums(id, limit=20)
        logging.debug(albums)





