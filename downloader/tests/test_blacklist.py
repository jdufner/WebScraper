import unittest
from downloader.blacklist import Blacklist


class BlacklistTestCase(unittest.TestCase):

    def test_is_listed_1(self):
        blacklist = Blacklist()
        self.assertTrue(blacklist.is_listed('http://www.heise.de/sso/'))

    def test_is_listed_2(self):
        blacklist = Blacklist()
        self.assertTrue(blacklist.is_listed('https://www.heise.de/sso/login'))

    def test_is_listed_3(self):
        blacklist = Blacklist()
        self.assertFalse(blacklist.is_listed('https://www.heise.de/'))

    def test_is_listed_4(self):
        blacklist = Blacklist()
        self.assertFalse(blacklist.is_listed('https://www.heise.de/newsticker'))


if __name__ == '__main__':
    unittest.main()
