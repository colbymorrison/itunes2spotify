from spotipy import SpotifyException
import os
import subprocess
import time
import logging
from itunes2spotify.album import Album
from itunes2spotify.menu import Menu
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
                    self.possible_matches = []
                    try:
                        self.search_albums()
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
        return [x.strip().lower() for x in ret_arr]

    # Updates instance variables if current itunes album has changed
    def album_changed(self):
        album_artist = self.get_itunes_album()

        if album_artist != ['', ''] and album_artist != self.get_album_artist():
            self.itunes_album = album_artist[0].strip().lower()
            self.itunes_artist = album_artist[1].strip().lower()
            return True
        else:
            return False

    def search_albums(self):
        try:
            album_results = self.sp.search(q='album:' + self.itunes_album, limit='20', type='album')
        except IndexError:
            return

        album_items = album_results['albums']['items']
        if not self.check_items(album_items):
            self.search_artists()

    def search_artists(self):
        try:
            artist_results = self.sp.search(q='artist:' + self.itunes_artist, type='artist')
            artist_id = artist_results['artists']['items'][0]['id']
        except IndexError:
            self.confirm_add_menu()
            return
        artist_items = self.sp.artist_albums(artist_id, limit=50)['items']
        if not self.check_items(artist_items):
            self.confirm_add_menu()

    def check_items(self, items):
        for spfy_album in items:
            if spfy_album['album_type'] == "single":
                continue

            album = Album.from_spfy_album(spfy_album)
            title = album.title.lower()

            if title == self.itunes_album and album.artist.lower() == self.itunes_artist:
                self.confirm_add_single(album)
                return True
            elif self.itunes_album in title:
                self.possible_matches.append(album)
        return False

    def confirm_add_menu(self):
        length = len(self.possible_matches)
        if length == 0:
            print("Sorry, couldn't find a matching album on Spotify\n")
        elif length == 1:
            self.confirm_add_single(self.possible_matches[0])
        else:
            menu = Menu(self.sp)
            menu.set_title("Found the following matching albums. Select an album to add to Spotify or None to exit")
            options = []
            for album in self.possible_matches:
                # TODO: WHY IS IT ADDING THE WRONG ALBUM??
                options.append(album)
            menu.set_options(options)
            menu.show()

    # Ask before adding if no-interactive flag is not set
    def confirm_add_single(self, album):
        if not self.flag:
            album.add_to_spotify(self.sp)
        else:
            print("Found {}".format(album.album_by_artist()))
            ans = input("Correct? (y/n): ")
            while True:
                if ans == 'y':
                    album.add_to_spotify(self.sp)
                    return True
                elif ans == 'n':
                    self.logger.debug("WRONG: {}".format(album.album_by_artist()))
                    return False
                else:
                    ans = input("Please enter y or n")

    # Useful for testing
    def get_album_artist(self):
        return [self.itunes_album, self.itunes_artist]


