import unittest
from webscraper.page_downloader.repository import Repository
from webscraper.page_downloader.repository import SqliteRepository


class RepositoryTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.config: dict = ({
            "database": {
                "type": "in-memory",
                "in-memory": {
                    "url": ":memory:",
                    "username": "",
                    "password": ""
                }
            }
        })

    def test_create_tables(self) -> None:
        # arrange
        repository: Repository = SqliteRepository(self.config)

        # act
        repository.create_tables()

        # assert
        table_name: str = 'documents'
        repository.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        self.assertEqual(table_name, repository.cursor.fetchone()[0], f"Table {table_name} doesn't exist.")
