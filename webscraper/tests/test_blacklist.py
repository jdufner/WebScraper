import unittest
from webscraper.blacklist import Blacklist


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

    def test_is_listed_5(self):
        blacklist = Blacklist()
        self.assertTrue(blacklist.is_listed('http://telepolis.de/'))

    def test_is_listed_6(self):
        blacklist = Blacklist()
        self.assertTrue(blacklist.is_listed('http://www.telepolis.de/'))

    def test_is_listed_7(self):
        blacklist = Blacklist()
        self.assertTrue(blacklist.is_listed('https://www.telepolis.de/features/Ukraine-Krieg-Die-neue-Aera-der-Kriegsfuehrung-fordert-Panzertechnik-heraus-9677501.html'))


if __name__ == '__main__':
    unittest.main()
