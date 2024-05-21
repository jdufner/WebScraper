import logging
import random
from abc import abstractmethod
from picturechoice.server.choice import Choice
import sqlite3


class Repository:
    def __init__(self, config: dict) -> None:
        self.config = config
        self.con = None
        self.cursor = None

    def __del__(self) -> None:
        self.con.close()

    @abstractmethod
    def create_tables(self) -> None:
        pass

    @abstractmethod
    def save_choice(self, choice: Choice) -> None:
        pass

    @abstractmethod
    def get_random_image(self) -> (int, str):
        pass


class SqliteRepository(Repository):
    def __init__(self, config: dict) -> None:
        super().__init__(config)
        if self.config["database"]["type"].lower() == "in-memory":
            self.con = sqlite3.connect(self.config["database"]["in-memory"]["url"])
        else:
            self.con = sqlite3.connect(self.config["database"]["sqlite3"]["url"], check_same_thread=False)
        self.cursor = self.con.cursor()
        self.create_tables()

    def create_tables(self) -> None:
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS choices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            provided_at DATETIME NOT NULL,
            answered_at DATETIME NOT NULL,
            first INTEGER NOT NULL,
            second INTEGER NOT NULL
        )''')

    def save_choice(self, choice: Choice) -> None:
        first_image_id = self.__read_image_id(choice.first)
        second_image_id = self.__read_image_id(choice.second)
        self.cursor.execute('INSERT INTO choices (provided_at, answered_at, first, second) VALUES (?, ?, ?, ?)',
                            (choice.provided, choice.answered, first_image_id, second_image_id))
        self.con.commit()

    def __read_image_id(self, filename) -> int:
        self.cursor.execute('SELECT id FROM images WHERE filename = ?', (filename,))
        return self.cursor.fetchone()[0]

    def get_random_image(self) -> (int, str):
        self.cursor.execute('SELECT id, filename FROM images WHERE downloaded = 1 ORDER BY RANDOM() LIMIT 10')
        return self.cursor.fetchone()[0], self.cursor.fetchone()[1]
