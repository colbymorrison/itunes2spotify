import spotipy
import spotipy.util as util
import os
import subprocess
import time


def spfy_sign_in(username):
    global sp
    scope = 'user-library-modify'
#    token = util.prompt_for_user_token(username, scope)
    token = util.prompt_for_user_token(username, scope, client_id='5af78a01d52c4bf1b57c1d46d150a5fa',
                                       client_secret='801fc3bd271147e7a8e7af69e96609d7',
                                       redirect_uri='http://localhost/')
    if token:
        sp = spotipy.Spotify(auth=token)
    else:
        print("Error: couldn't access token")


def get_itunes_album():
    itpath = "/opt/itunescli/build/Release/iTunescli"
    process = subprocess.Popen([itpath, 'info'], stdout=subprocess.PIPE)
    return str(process.communicate()[0], 'utf-8')


def add_to_lib():
    results = sp.search(q="album:"+get_itunes_album(), type='album')
    items = results['albums']['items'][0]
    album_id = items['uri']

    album_name = items['name']
    artist_name = items['artists'][0]['name']

    album = sp.album(album_id)
    sp.current_user_saved_albums(album)

    print(results)
    print(artist_name)
    print(album_name)


def main():
    spfy_sign_in("colbyacts@gmail.com")
    add_to_lib()


if __name__ == "__main__":
    main()

