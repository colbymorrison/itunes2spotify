import spotipy
import click
import os
import sys
#from itunes2spotify.transfer import Transfer
from transfer import Transfer
from spotipy import util
from spotipy.client import SpotifyException
from pathlib import Path
import logging

file_path = Path(os.path.dirname(os.path.abspath(__file__)))
resource_path = file_path / 'resources'
logs_path = file_path.parent / 'logs.log'
token_path = resource_path / 'token'


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

    with open(resource_path / 'client_secret', 'r') as f:
        client_id = f.readline().rstrip()
        client_secret = f.readline().rstrip()

    token = util.prompt_for_user_token(username, scope=scope, client_id=client_id,
                                       client_secret=client_secret,
                                       redirect_uri='http://localhost/')
    if token:
        with open(token_path, 'w') as f:
            f.write(token)
        success = "Successfully logged in {}".format(username)
        logger.info(success)
        print(success)
    else:
        logger.error("Login error")
        print("Login error, Please try again")


# Start transfer
@its.command(help='Initiate transfer')
@click.option('--risk', '-r', is_flag=True,
              help='Will not ask for confirmation Spotify album is correct before adding')
def transfer(risk):
    with open(token_path, 'r') as f:
        token = f.read()

    if not token:
        logger.error("Unable to authenticate")
        print("Unable to authenticate. Please login with the 'login' command")
        return
    else:
        try:
            sp = spotipy.Spotify(auth=token)
        except SpotifyException:
            logger.error("Soptify error")
            print("Soptify error. Please try log in again and retry")
            return

    if risk:
        tran = Transfer(sp, False)
    else:
        tran = Transfer(sp, True)

    logger.debug("Starting transfer")
    tran.start()


def main():
    global logger
    log_form = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(filename=logs_path, format=log_form, level=logging.DEBUG)
    logger = logging.getLogger()
    logger.debug("Start")
    its()


if __name__ == "__main__":
    main()
