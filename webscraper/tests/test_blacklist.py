import unittest
from webscraper.blacklist import Blacklist


class BlacklistTestCase(unittest.TestCase):

    def setUp(self):
        self.urls = [
            "http://www.heise.de/account/cancellation",
            "http://www.heise.de/benachrichtigungen/",
            "http://www.heise.de/kontakt/",
            "http://www.heise.de/loseblattwerke/",
            "http://www.heise.de/news-extern/news.html",
            "http://www.heise.de/newsletter/",
            "http://www.heise.de/plus/",
            "http://www.heise.de/preisvergleich/",
            "http://www.heise.de/select/",
            "http://www.heise.de/sso/",
            "http://www.heise.de/tarifrechner/",
            "http://www.heise.de/tools/",
            "http://www.heise.de/themen/",
            "https://blog.heise-academy.de/",
            "https://business-services.heise.de/",
            "https://compaliate.heise.de/",
            "https://facebook.com/heiseonline",
            "https://heise-academy.de/",
            "https://it-kenner.heise.de/",
            "https://jobs.heise.de/",
            "https://kiupdate.podigee.io/episodes",
            "https://kurzinformiert.podigee.io/episodes",
            "https://m.me/heiseonline",
            "https://mediadaten.heise.de/",
            "https://pubads.g.doubleclick.net/",
            "https://security-tour.heise.de/",
            "https://shop.heise.de/",
            "https://spiele.heise.de/",
            "https://survey.vocatus.de/",
            "https://t3n.de/",
            "https://telepolis.de/",
            "https://twitter.com/heiseonline",
            "https://www.geizhals.at/",
            "https://www.heise-gruppe.de/",
            "https://www.heise-regioconcept.de/",
            "https://www.heise.de/download",
            "https://www.heise.de/forum",
            "https://www.heise.de/kontakt/",
            "https://www.heise.de/sso/",
            "https://www.hostg.xyz/",
            "https://www.interred.de/",
            "https://www.plusline.net/",
            "https://www.techstage.de/",
            "https://www.telepolis.de/",
            "https://www.xing.com/",
            "http://www.heise.de/api/"
        ]

    def test_is_listed_1(self):
        blacklist = Blacklist(self.urls)
        self.assertTrue(blacklist.is_listed('http://www.heise.de/sso/'))

    def test_is_listed_2(self):
        blacklist = Blacklist(self.urls)
        self.assertTrue(blacklist.is_listed('https://www.heise.de/sso/login'))

    def test_is_listed_3(self):
        blacklist = Blacklist(self.urls)
        self.assertFalse(blacklist.is_listed('https://www.heise.de/'))

    def test_is_listed_4(self):
        blacklist = Blacklist(self.urls)
        self.assertFalse(blacklist.is_listed('https://www.heise.de/newsticker'))

    def test_is_listed_5(self):
        blacklist = Blacklist(self.urls)
        self.assertTrue(blacklist.is_listed('http://telepolis.de/'))

    def test_is_listed_6(self):
        blacklist = Blacklist(self.urls)
        self.assertTrue(blacklist.is_listed('http://www.telepolis.de/'))

    def test_is_listed_7(self):
        blacklist = Blacklist(self.urls)
        self.assertTrue(blacklist.is_listed('https://www.telepolis.de/features/Ukraine-Krieg-Die-neue-Aera-der-Kriegsfuehrung-fordert-Panzertechnik-heraus-9677501.html'))


if __name__ == '__main__':
    unittest.main()
