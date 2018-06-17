import sys
import spotipy
import click
from transfer import Transfer
from spotipy import util


# Startup
@click.group()
@click.option('--version', '-v', is_flag=True, help='Display current version')
def its(version):
    if version:
        print("iTunes2Spotify v0.1.0")\



# Start transfer
@its.command(help='Initiate transfer')
@click.option('--risk', '-r', is_flag=True,
              help='Will not ask for confirmation Spotify album is correct before adding')
def tran(risk):
    with open('username', 'r') as f:
        token = f.read()
    if token == "":
        print("Unable to authenticate. Please login with the 'login' command")
        return
    else:
        sp = spotipy.Spotify(auth=token)

    if risk:
        transfer = Transfer(sp, False)
    else:
        transfer = Transfer(sp, True)

    transfer.start()


# Log into Spotify
@its.command()
@click.argument('username')
def login(username):
    scope = 'user-library-modify'

    # token = util.prompt_for_user_token(username, scope)
    token = util.prompt_for_user_token(username, scope=scope, client_id='',
                                       client_secret='',
                                       redirect_uri='http://localhost/')
    if token:
        with open('username', 'w') as f:
            f.write(token)
        print("Succesfully logged in {}".format(username))  # current_user() ?
    else:
        print("Error accessing token, please try again")


if __name__ == "__main__":
    its()
