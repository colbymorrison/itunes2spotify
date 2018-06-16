import spotipy
import spotipy.util as util
import os

def spfy_sign_in(username):
    scope = 'user-library-modify'
#    token = util.prompt_for_user_token(username, scope)
    token = util.prompt_for_user_token(username, scope, client_id=os.environ['SPOTIPY_CLIENT_ID'], client_secret=os.environ['SPOTIPY_CLIENT_SECRET'], redirect_uri=os.environ['SPOTIPY_REDIRECT_URI'])
    if token:
        sp = spotipy.Spotify(auth=token)
    else:
        print("Error: couldn't access token")
    results = sp.search(q="Ye", limit=1, type='album')
    print(results)

spfy_sign_in("colbyacts@gmail.com")
