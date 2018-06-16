import spotipy
import spotipy.util as util
import os
import subprocess
import time
from pathlib import Path


# Startup
def welcome():
    # TODO: make this good
    print("Hello!")
    username = input("Please enter your Spotify username: ")
    spfy_go(username)


# Log into Spotify
def spfy_go(username):
    global sp
    global token
    scope = 'user-library-modify'
#    token = util.prompt_for_user_token(username, scope)
    token = util.prompt_for_user_token(username, scope=scope, client_id='5af78a01d52c4bf1b57c1d46d150a5fa',
                                       client_secret='11e1c6dc70e048bb8bbd0516bdded1ae',
                                       redirect_uri='http://localhost/')
    if token:
        sp = spotipy.Spotify(auth=token)
        # TODO: How do you quit this?
        start_transfer()

    else:
        print("Error: couldn't access token")


def start_transfer():
    print("Ready.\nPlay album in iTunes to transfer (CTRL-C to stop)")
    try:
        curr_album = get_itunes_album()
        changed = True
        new_album = curr_album
        while True:
            if changed:
                get_spotify_album(new_album)
            else:
                time.sleep(5)
            changed, new_album = album_changed(curr_album)
    except KeyboardInterrupt:
        return 0



def album_changed(album):
    new_album = get_itunes_album()
    if album != new_album:
        return True, new_album
    else:
        return False, None




def get_itunes_album():
    ROOT_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
    process = subprocess.Popen(["swift", str(ROOT_DIR.parent / 'utils' / 'album.swift')],
                               stdout=subprocess.PIPE)
    return str(process.communicate()[0], 'utf-8')


def get_spotify_album(it_album_str):
    results = sp.search(q="album:" + it_album_str, type='album')
    items = results['albums']['items'][0]
    album_id = items['uri']

    album_name = items['name']
    artist_name = items['artists'][0]['name']

    spfy_album = sp.album(album_id)

    print("Found {} by {}".format(album_name, artist_name))
    flag = True

    # TODO: flag
    if flag:
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



def main():
    #welcome()
    spfy_go("colbyacts@gmail.com")
    #start_transfer()
    #print(get_itunes_album())


if __name__ == "__main__":
    main()

