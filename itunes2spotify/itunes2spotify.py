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




def main():
    #welcome()
    spfy_go("colbyacts@gmail.com")
    #start_transfer()
    #print(get_itunes_album())


if __name__ == "__main__":
    main()

