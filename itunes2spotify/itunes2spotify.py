import spotipy
import spotipy.util as util
import os
import subprocess
import time


def spfy_sign_in(username):
    global sp
    scope = 'user-library-modify'
#    token = util.prompt_for_user_token(username, scope)
    token = util.prompt_for_user_token(username, scope, client_id=os.environ['SPOTIPY_CLIENT_ID'],
                                       client_secret=os.environ['SPOTIPY_CLIENT_SECRET'],
                                       redirect_uri=os.environ['SPOTIPY_REDIRECT_URI'])
    if token:
        sp = spotipy.Spotify(auth=token)
    else:
        print("Error: couldn't access token")


def get_itunes_album():
    itpath = "/opt/itunescli/build/Release/iTunescli"
    process = subprocess.Popen([itpath, 'info'], stdout=subprocess.PIPE)
    return process.communicate()[0]


def add_to_lib():
    results = sp.search(get_itunes_album(), type='album')
    print(results)


def main():
    spfy_sign_in("colbyacts@gmail.com")
    add_to_lib()

if __name__ == "__main__":
    main()
