import spotipy
import spotipy.util as util
import os
import subprocess
import time
from pathlib import Path

# Transfer iTunes album that is playing to Spotify library


class Transfer:
    def __init__(self, username, flag):
        self.username = username
        self.flag = flag
        self.sp = None

    # Log into Spotify
    def spfy_go(self):
        scope = 'user-library-modify'
        with open('client_secret', 'r') as file:
            client_id = file.readline()
            client_secret = file.readline()
    #    token = util.prompt_for_user_token(username, scope)
        token = util.prompt_for_user_token(self.username, scope=scope, client_id=client_id,
                                           client_secret=client_secret,
                                           redirect_uri='http://localhost/')
        if token:
            self.sp = spotipy.Spotify(auth=token)
            # TODO: How do you quit this?
            try:
                self.start_transfer()
            except KeyboardInterrupt:
                return 0
        else:
            print("Error: couldn't access token")

    # Checks if iTunes album has changed every 5 seconds, if it has add to Spotify
    def start_transfer(self):
        print("Ready.\nPlay album in iTunes to transfer (CTRL-C to quit)")
        curr_album = self.get_itunes_album()
        changed = True
        new_album = curr_album
        while True:
            if changed:
                self.get_spotify_album(new_album)
            else:
                time.sleep(5)
            changed, new_album = self.album_changed(curr_album)

    # Given an album, it is not playing in iTunes?
    def album_changed(self, album):
        new_album = self.get_itunes_album()
        if album != new_album:
            return True, new_album
        else:
            return False, None

    # Call to Swift function
    def get_itunes_album(self):
        ROOT_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
        process = subprocess.Popen(["swift", str(ROOT_DIR.parent / 'utils' / 'album.swift')],
                                   stdout=subprocess.PIPE)
        return str(process.communicate()[0], 'utf-8')

    # Search for album string in Spotify and add to library
    def get_spotify_album(self, it_album_str):
        results = self.sp.search(q="album:" + it_album_str, type='album')
        items = results['albums']['items'][0]
        album_id = items['uri']

        album_name = items['name']
        artist_name = items['artists'][0]['name']

        spfy_album = self.sp.album(album_id)

        print("Found {} by {}".format(album_name, artist_name))
        flag = True

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

        print("Adding...")
        #sp.current_user_saved_albums(spfy_album)
        return
