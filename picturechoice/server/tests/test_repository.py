from picturechoice.server.repository import Repository, SqliteRepository
import unittest


class RepositoryTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.config: dict = ({
            "database": {
                "_types": ["in-memory", "sqlite3"],
                "type": "sqlite3",
                "in-memory": {
                    "url": ":memory:",
                    "username": "",
                    "password": ""
                },
                "sqlite3": {
                    "url": " ../../heise_sqlite3.db",
                    "username": "",
                    "password": ""
                }
            }
        })

    def test_when_init_expect_answered_initialized(self):
        # arrange
        repository: Repository = SqliteRepository(self.config)

        # act
        repository.get_random_image()

        # assert

