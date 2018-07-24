import unittest
import spotipy
from unittest.mock import MagicMock
from album import Album
from menu import Menu


class MenuTest(unittest.TestCase):

    # I know this isn't really a unit test
    def test_options(self):
        sp = MagicMock(spotipy.Spotify())
        album1 = Album("Abbey Road", "The Beatles", "1")
        album2 = Album("Liquid Swords", "GZA", "2")
        album3 = Album("In the Aeroplane Over the Sea", "Neutral Milk Hotel", "3")
        album4 = Album("Highway 61 Revisited", "Bob Dylan", "4")
        album5 = Album("Year of the Snitch", "Death Grips", "5")
        album6 = Album("Madvilaiany", "Madvillain", "6")

        options = [album1, album2, album3, album4, album5, album6]

        menu = Menu(sp)

        menu.set_options(options)
        menu.show()



