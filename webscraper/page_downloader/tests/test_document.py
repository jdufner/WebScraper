import unittest
from datetime import datetime
from webscraper.page_downloader.document import Document


class RepositoryTestCase(unittest.TestCase):
    def setUp(self) -> None:
        pass

    def test_when_created_at_is_empty_expect_empty_string(self) -> None:
        # arrange
        document = Document('http://www.domain.tld/', '<html></html>', 'title', datetime.now(), [], [], [], [], [])

        # act
        created_at: datetime = document.created_at_or_none()

        # assert
        self.assertIsNone(created_at)

    def test_when_created_at_is_there_expect_iso_string(self) -> None:
        # arrange
        iso_date: str = '2023-12-01'
        document = Document('http://www.domain.tld/', '<html></html>', 'title', datetime.now(), [iso_date], [], [], [], [])

        # act
        created_at: datetime = document.created_at_or_none()

        # assert
        self.assertEqual(datetime.fromisoformat(iso_date), created_at)

    def test_when_creators_is_empty_expect_none(self) -> None:
        # arrange
        document = Document('http://www.domain.tld/', '<html></html>', 'title', datetime.now(), [], [], [], [], [])

        # act
        created_by: str = document.created_by_as_string()

        # assert
        self.assertIsNone(created_by)

    def test_when_one_creator_is_there_expect_one(self) -> None:
        # arrange
        name1: str = 'First name1 Name1'
        document = Document('http://www.domain.tld/', '<html></html>', 'title', datetime.now(), [], [name1], [], [], [])

        # act
        created_by: str = document.created_by_as_string()

        # assert
        self.assertEqual(name1, created_by)

    def test_when_two_creators_are_there_expect_comma_separated_string(self) -> None:
        # arrange
        name1: str = 'First name1 Name1'
        name2: str = 'First name2 Name2'
        document = Document('http://www.domain.tld/', '<html></html>', 'title', datetime.now(), [], [name1, name2], [], [], [])

        # act
        created_by: str = document.created_by_as_string()

        # assert
        self.assertEqual(name1 + ', ' + name2, created_by)
