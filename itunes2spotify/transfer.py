from spotipy import SpotifyException
import spotipy.util as util
import os
import subprocess
import time
import logging
import json
from datetime import datetime
from datetime import timedelta
from menu import Menu
from pathlib import Path

# Transfer iTunes album that is playing to Spotify library

file_path = Path(os.path.dirname(os.path.abspath(__file__)))
logs_path = file_path.parent / 'logs.log'


class Transfer:

    def __init__(self, sp, flag):
        # Is -r option set?
        self.flag = flag
        # Connection to Spotify, Spotify client object
        self.sp = sp
        # Connection to iTunes
        self.curr_album_artist = None

        # Set up logger
        log_form = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        logging.basicConfig(filename=logs_path, format=log_form, level=logging.DEBUG)
        logger = logging.getLogger()
        logger.debug("Start")
        self.logger = logging.getLogger(__name__)

    # Called by transfer script
    def start(self):
        while True:
            try:
                if self.album_changed():
                    self.logger.debug("New iTunes album artist: {}".format(self.curr_album_artist[1]))
                    try:
                        print("Play album in iTunes to transfer (CTRL-C to quit)")
                        self.get_spotify_matches(self.curr_album_artist[0])
                    except IndexError:
                        print("Couldn't find an album with this title in Spotify")
                    except SpotifyException:
                        self.logger.error("Soptify error")
                        print("Soptify error. Please try log in again and retry")
                else:
                    time.sleep(2)
            except KeyboardInterrupt:
                return 0

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
    def get_spotify_matches(self, it_album_str):
        itunes_album = self.curr_album_artist[0]
        itunes_artist = self.curr_album_artist[1]

        # First search for album directly on Spotify, on avg. takes about
        start = datetime.now()
        results = self.sp.search(q="album:" + it_album_str, type='album')
        items = results['albums']['items'][0]

        artist_name = items['artists'][0]['name'].strip()
        album_name = items['name']

        logging.debug("TIMING: dsearch {}".format((start - datetime.now()) / timedelta(milliseconds=1)))
        if artist_name == itunes_artist and album_name == itunes_album:
            album_matches = {album_name: items['uri']}
        else:
            album_matches = self.search_artist()

        if len(album_matches) == 0:
            print("Spotify has no albums containing the name \"{}\" by \"{}\"".format(self.curr_album_artist[0],
                                                                                      self.curr_album_artist[1]))
        else:
            self.get_spotify_album(album_matches)

    def get_spotify_album(self, albums_dict):
        if len(albums_dict) == 1:
            album_name = list(albums_dict.keys())[0]
            print("Found {} by {}".format(album_name, self.curr_album_artist[1]))
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
                self.add_spotify_album(album_name, albums_dict[album_name])
        else:
            menu = Menu()
            menu.set_title("Found the following matching albums by {}.\
                           Select an album to add to Spotify or None to exit"
                           .format(self.curr_album_artist[1]))
            options = []
            for item in albums_dict.items():
                options.append((item[0], lambda name=item[0], album_id=item[1]: self.add_spotify_album(name, album_id)))
            options.append(("None", menu.close))
            menu.set_options(options)
            menu.set_refresh(menu.close)
            menu.open()

    def add_spotify_album(self, album_name, album_id):
        print("Adding {} by {} \n".format(album_name, self.curr_album_artist[1]))
        # self.sp.current_user_saved_albums_add([album_id])
        return

    # Search through an artist's albums on spotify until one matches iTunes album name
    def search_artist(self):
        album_match = {}
        itunes_album = self.curr_album_artist[0]
        artist = self.curr_album_artist[1]

        self.logger.debug("Artist: {}".format(artist))
        results = self.sp.search(q=artist, type='artist')

        album_id = results['artists']['items'][0]['id']
        albums = self.sp.artist_albums(album_id, limit=50)
        album_items = albums['items']

        for album in album_items:
            new_album = album['name']
            if new_album == itunes_album:
                album_match = {new_album: album['id']}
                break
            elif itunes_album in new_album:
                album_match[new_album] = album['id']

        return album_match
