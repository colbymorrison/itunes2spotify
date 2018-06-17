import unittest
from unittest.mock import MagicMock
from transfer import Transfer
import spotipy


class TransferTest(unittest.TestCase):
    def setUp(self):
        sp = MagicMock(spotipy.Spotify())
        self.transfer = Transfer(sp, True)
        self.transfer.get_itunes_album = MagicMock(return_value='Abbey Road')

    def test_changed_None_Some(self):
        album = None

        changed, new = self.transfer.album_changed(album)
        self.assertTrue(changed)
        self.assertEqual(new, 'Abbey Road')

    def test_changed_Some_Some(self):
        album = 'Revolver'

        changed, new = self.transfer.album_changed(album)
        self.assertTrue(changed)
        self.assertEqual(new, 'Abbey Road')


    def test_changed_None_None(self):
        self.transfer.get_itunes_album = MagicMock(return_value=None)
        album = None

        changed, new = self.transfer.album_changed(album)
        self.assertFalse(changed)

    def test_changed_Some_None(self):
        self.transfer.get_itunes_album = MagicMock(return_value=None)
        album = 'Abbey Road'

        changed, new = self.transfer.album_changed(album)
        self.assertFalse(changed)


