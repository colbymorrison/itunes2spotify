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

    def start(self):
        while True:
            try:
                self.run_transfer()
            except KeyboardInterrupt:
                return 0

    # Checks if iTunes album has changed every 2 seconds, if it has add to Spotify
    def run_transfer(self):
        if self.album_changed():
            self.logger.debug("New iTunes album artist: {}".format(self.curr_album_artist[1]))
            try:
                print("Play album in iTunes to transfer (CTRL-C to quit)")
                self.get_spotify_album(self.curr_album_artist[0])
            except IndexError:
                print("Couldn't find an album with this title in Spotify")
            except SpotifyException:
                self.logger.error("Soptify error")
                print("Soptify error. Please try log in again and retry")
        else:
            time.sleep(2)

    # Runs swift script to get current album and artist from iTunes
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

    # Search for album in Spotify and add to library
    def get_spotify_album(self, it_album_str):
        # Search for album
        results = self.sp.search(q="album:" + it_album_str, type='album')
        items = results['albums']['items'][0]

        album_id = items['uri']
        album_name = items['name']
        artist_name = items['artists'][0]['name']

        # Is found album's artist same as iTunes artist?
        if artist_name.strip() != self.curr_album_artist[1].strip():
            self.logger.debug("Artist name {}, itunes artist {}".format(artist_name, self.curr_album_artist[1]))
            try:
                album_name, album_id = self.search_artist()
            except TypeError:
                return

        print("Found {} by {}".format(album_name, artist_name))

        # If -r mode is not set, check if correct album was found
        if self.flag:
            while True:
                ans = input("Correct? (y/n): ")
                if ans == 'y':
                    break
                elif ans == 'n':
                    print("Sorry!")
                    return
                else:
                    print("Please enter y or n")

        print("Adding {} by {} \n".format(album_name, artist_name))
        self.sp.current_user_saved_albums_add([album_id])
        return

    # Search through an artist's albums on spotify until one matches iTunes album name
    def search_artist(self):
        artist = self.curr_album_artist[1]

        self.logger.debug("Artist: {}".format(artist))
        results = self.sp.search(q=artist, type='artist')

        album_id = results['artists']['items'][0]['id']
        albums = self.sp.artist_albums(album_id, limit=50)
        album_items = albums['items']

        for album in album_items:
            new_album = album['name']
            if new_album == self.curr_album_artist[0]:
                return new_album, album['id']
            
        print("Spotify has no albums with the name {} by {}".format(self.curr_album_artist[0],
                                                                    self.curr_album_artist[1]))
        # TODO: Custom error for no albums?
        return None







