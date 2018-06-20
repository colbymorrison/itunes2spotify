import spotipy
import click
import os
from itunes2spotify.transfer import Transfer
# from transfer import Transfer
from spotipy import util
from spotipy.client import SpotifyException
from pathlib import Path


file_path = Path(os.path.dirname(os.path.abspath(__file__)))
userfile = file_path.parent / 'resources' / 'token'


# Startup
@click.group()
@click.option('--version', '-v', is_flag=True, help='Display current version')
def its(version):
    if version:
        print("iTunes2Spotify v0.1.0")


# Log into Spotify
@its.command(help='Login to Spotify with your username')
@click.argument('username')
def login(username):
    scope = 'user-library-modify'

    with open(file_path.parent/'resources'/'client_secret', 'r') as f:
        client_id = f.readline().rstrip()
        client_secret = f.readline().rstrip()

    token = util.prompt_for_user_token(username, scope=scope, client_id=client_id,
                                       client_secret=client_secret,
                                       redirect_uri='http://localhost/')
    if token:
        with open(userfile, 'w') as f:
            f.write(token)
        print("Successfully logged in {}".format(username))
    else:
        print("Error accessing token, please try again")


# Start transfer
@its.command(help='Initiate transfer')
@click.option('--risk', '-r', is_flag=True,
              help='Will not ask for confirmation Spotify album is correct before adding')
def tran(risk):
    with open(userfile, 'r') as f:
        token = f.read()

    if not token:
        print("Unable to authenticate. Please login with the 'login' command")
        return
    else:
        try:
            sp = spotipy.Spotify(auth=token)
        except SpotifyException:
            print("Sorry there was an error, please try log in again and retry")
            return

    if risk:
        transfer = Transfer(sp, False)
    else:
        transfer = Transfer(sp, True)

    transfer.start()


def main():
    its()


if __name__ == "__main__":
    main()
