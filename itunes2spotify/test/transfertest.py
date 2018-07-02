import unittest
from unittest.mock import MagicMock
from transfer import Transfer
import spotipy


class TransferTest(unittest.TestCase):
    def setUp(self):
        sp = MagicMock(spotipy.Spotify())
        self.transfer = Transfer(sp, True)

        self.abbey_road = ['Abbey Road', 'The Beatles']
        self.transfer.get_itunes_album = MagicMock(return_value=self.abbey_road)
        self.transfer.curr_album_artist = None

    def test_changed_None_Some(self):
        changed = self.transfer.album_changed()
        self.assertTrue(changed)
        self.assertEqual(self.transfer.get_album_artist(), self.abbey_road)

    def test_changed_Some_Some(self):
        self.transfer.curr_album_artist = ['Revolver', 'The Beatles']

        changed = self.transfer.album_changed()
        self.assertTrue(changed)
        self.assertEqual(self.transfer.get_album_artist(), self.abbey_road)

    def test_changed_None_None(self):
        self.transfer.album_changed = MagicMock(return_value=None)

        changed = self.transfer.album_changed()
        self.assertFalse(changed)

    def test_changed_Some_None(self):
        self.transfer.album_changed = MagicMock(return_value=None)
        self.transfer.curr_album_artist = self.abbey_road

        changed = self.transfer.album_changed()
        self.assertFalse(changed)




