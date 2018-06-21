from spotipy import SpotifyException
import spotipy.util as util
import os
import subprocess
import time
import logging
import json
from pathlib import Path


# Transfer iTunes album that is playing to Spotify library

file_path = Path(os.path.dirname(os.path.abspath(__file__)))
logs_path = file_path.parent / 'logs.log'


class Transfer:

    def __init__(self, sp, flag):
        self.flag = flag
        self.sp = sp
        self.curr_album_artist = None

        log_form = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        logging.basicConfig(filename=logs_path, format=log_form, level=logging.DEBUG)
        logger = logging.getLogger()
        logger.debug("Start")
        self.logger = logging.getLogger(__name__)

    # Checks if iTunes album has changed every 5 seconds, if it has add to Spotify
    def start(self):
        while True:
            try:
                if self.album_changed():
                    logging.debug("Album artist {}".format(self.curr_album_artist[1]))
                    try:
                        self.get_spotify_album(self.curr_album_artist[0])
                        print("Play album in iTunes to transfer (CTRL-C to quit)")
                    except IndexError:
                        print("Couldn't find an album with this title in Spotify")
                    except SpotifyException:
                        self.logger.error("Soptify error")
                        print("Soptify error. Please try log in again and retry")
                else:
                    time.sleep(1)
            except KeyboardInterrupt:
                return 0

    @staticmethod
    def get_itunes_album():
        process = subprocess.Popen(["swift", str(file_path / 'resources' / 'album.swift')],
                                   stdout=subprocess.PIPE)
        return str(process.communicate()[0], 'utf-8').split('<')


    def album_changed(self):
        album_artist = self.get_itunes_album()

        if album_artist and album_artist != self.curr_album_artist:
            self.curr_album_artist = album_artist
            return True
        else:
            return False


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
                    print("Adding {} by {} \n".format(album_name, artist_name))
                    break
                elif ans == 'n':
                    album_name, album_id = self.search_artist()
                    if album_name is None:
                        print("Spotify has no albums by {} with the name {}".format(artist_name,
                                                                                    self.curr_album_artist[0]))
                        break
                    else:
                        print("Found {} by {}".format(self.curr_album_artist[0], artist_name))
                else:
                    print("Please enter y or n")

        self.sp.current_user_saved_albums_add([album_id])
        return

    def search_artist(self):
        artist = self.curr_album_artist[1]

        logging.debug("Artist: {}".format(artist))
        results = self.sp.search(q=artist, type='artist')

        id = results['artists']['items'][0]['id']
        albums = self.sp.artist_albums(id, limit=50)
        items = albums['items']

        for album in items:
            name = album['name']
            logging.debug("Found album {}".format(name))
            if name == self.curr_album_artist[0]:
                return name, album['id']
        return None, False







