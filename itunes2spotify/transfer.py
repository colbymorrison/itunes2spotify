from spotipy import SpotifyException
import os
import subprocess
import time
import logging
from album import Album
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
        self.itunes_album = ""
        self.itunes_artist = ""
        # List of Album objects
        self.possible_matches = []

        # Set up logger
        log_form = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        logging.basicConfig(filename=logs_path, format=log_form, level=logging.DEBUG)
        self.logger = logging.getLogger(__name__)

    # Called by transfer script
    def start(self):
        print("Play album in iTunes to transfer (CTRL-C to quit)")
        while True:
            try:
                if self.album_changed():
                    try:
                        print("Play album in iTunes to transfer (CTRL-C to quit)")
                        self.get_spotify_matches()
                    except IndexError:
                        print("Couldn't find an album with this title in Spotify")
                    except SpotifyException:
                        self.logger.error("Soptify error")
                        print("Unable to authenticate Spotify account. Please log in again with the 'login' command and"
                              " retry")
                else:
                    time.sleep(3)
            except KeyboardInterrupt:
                print("\nGoodbye!")
                return 0

    # Runs swift script to get current album and artist from iTunes
    @staticmethod
    def get_itunes_album():
        process = subprocess.Popen(["swift", str(file_path / 'resources' / 'album.swift')],
                                   stdout=subprocess.PIPE)
        ret_arr = str(process.communicate()[0], 'utf-8').split('<')
        return [x.strip() for x in ret_arr]

    # Updates instance variables if current itunes album has changed
    def album_changed(self):
        album_artist = self.get_itunes_album()

        if album_artist != ['', ''] and album_artist != self.get_album_artist():
            self.logger.debug("ALBUM ARTIST CHANGED: from {} to {} ".format(self.get_album_artist(), album_artist))
            self.itunes_album = album_artist[0].strip()
            self.itunes_artist = album_artist[1].strip()
            return True
        else:
            return False

    # Search for album in Spotify
    def get_spotify_matches(self):
        # Search for albums with matching names on Spotify
        results = self.sp.search(q="album:" + self.itunes_album, limit='20', type='album')
        items = results['albums']['items']
        first_match = items[0]

        artist_name = first_match['artists'][0]['name'].strip()
        album_name = first_match['name'].strip()

        # If first album is a direct match (happens often), confirm and add
        if artist_name == self.itunes_artist and album_name == self.itunes_album:
            if self.confirm_add_single(Album(album_name, artist_name, first_match['id'])):
                return
        else:
            # If not, search through artist's albums and albums with matching name
            for album_obj in items:
                if album_obj['album_type'] != 'single':
                    self.possible_matches.append(Album
                                                 (album_obj['name'], album_obj['artists'][0]['name'], album_obj['id']))
            self.deep_search()

    # Search through an artist's albums on spotify until one matches iTunes album name
    def deep_search(self):
        results = self.sp.search(q=self.itunes_artist, type='artist')
        artist_id = results['artists']['items'][0]['id']
        artist_items = self.sp.artist_albums(artist_id, limit=50)['items']

        for album_obj in artist_items:
            album_name = album_obj['name']
            # If direct match is found, confirm and add
            if album_name == self.itunes_album:
                self.confirm_add_single(Album(album_name, self.itunes_artist, album_obj['id']))
                return
            elif self.itunes_album in album_name:
                self.possible_matches.append(Album(album_name, self.itunes_artist, album_obj['id']))

        self.confirm_add_menu()

    def confirm_add_menu(self):
        length = len(self.possible_matches)
        if length == 0:
            print("Spotify has no albums containing the name \"{}\" by \"{}\"".format(self.itunes_album,
                                                                                      self.itunes_artist))
        elif length == 1:
            self.confirm_add_single(self.possible_matches[0])
        else:
            menu = Menu()
            menu.set_title("Found the following matching albums. Select an album to add to Spotify or None to exit")
            options = []
            for album in self.possible_matches:
                options.append(("{} by {}".format(album.title, album.artist),
                                lambda: album.add_to_spotify(self.sp)))
            options.append(("None", menu.close))
            menu.set_options(options)
            menu.set_refresh(menu.close)
            menu.open()

    # Ask before adding if no-interactive flag is not set
    def confirm_add_single(self, album):
        print("Found {} by {}".format(album.title, album.artist))
        if not self.flag:
            album.add_to_spotify(self.sp)
        else:
            ans = input("Correct? (y/n): ")
            while True:
                if ans == 'y':
                    album.add_to_spotify(self.sp)
                    return True
                elif ans == 'n':
                    return False
                else:
                    ans = input("Please enter y or n")

    # Useful for testing
    def get_album_artist(self):
        return [self.itunes_album, self.itunes_artist]


