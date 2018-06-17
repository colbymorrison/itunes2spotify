import spotipy
import click
from transfer import Transfer
from spotipy import util
import pathlib
import os
from pathlib import Path
import json

file_path = Path(os.path.dirname(os.path.abspath(__file__)))
userfile = file_path / 'loggedin'


# Startup
@click.group()
@click.option('--version', '-v', is_flag=True, help='Display current version')
def its(version):
    if version:
        print("iTunes2Spotify v0.1.0")


# Log into Spotify
@its.command(help='Login to the service, enter your username')
@click.argument('username')
def login(username):
    scope = 'user-library-modify'

    token = util.prompt_for_user_token(username, scope=scope, client_id='5af78a01d52c4bf1b57c1d46d150a5fa',
                                       client_secret='6bcc348f9cda40fa8a8a46edca760c6b',
                                       redirect_uri='http://localhost/')
    if token:
        with open(userfile, 'w') as f:
            f.write(token)
        print("Successfully logged in {}".format(username))  # current_user() ?    else:
    else:
        print("Error accessing token, please try again")


# Start transfer
@its.command(help='Initiate transfer')
@click.option('--risk', '-r', is_flag=True,
              help='Will not ask for confirmation Spotify album is correct before adding')
def tran(risk):
    with open(userfile, 'r') as f:
        token = f.read()
    # token = get_cache(username)

    if not token:
        print("Unable to authenticate. Please login with the 'login' command")
        return
    else:
        sp = spotipy.Spotify(auth=token)

    if risk:
        transfer = Transfer(sp, False)
    else:
        transfer = Transfer(sp, True)

    transfer.start()


def get_cache(username):
    path = file_path / '.cache-{}'.format(username)
    if path.is_file():
        with open(path, 'r') as f:
            line = json.loads(f.read())
            return line['access_token']
    else:
        return None


def logout():
    with open(userfile, 'rw') as f:
        name = f.read()
        f.write("")
        print("Logged out {}".format(name))


if __name__ == "__main__":
    its()
