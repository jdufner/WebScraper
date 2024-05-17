import random
from abc import abstractmethod
from picturechoice.server.choice import Choice
import sqlite3


class Repository:
    def __init__(self, config: dict) -> None:
        self.config = config
        self.con = None
        self.cursor = None
        self.number_images = 0

    def __del__(self) -> None:
        self.con.close()

    @abstractmethod
    def create_tables(self) -> None:
        pass

    @abstractmethod
    def save(self, choice: Choice) -> None:
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
            self.con = sqlite3.connect(self.config["database"]["sqlite3"]["url"])
        self.cursor = self.con.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS choices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            provided_at DATETIME NOT NULL,
            answered_at DATETIME NOT NULL,
            first INTEGER NOT NULL,
            second INTEGER NOT NULL
        )''')

    def save(self, choice: Choice):
        first_image_id = self.__read_image_id(choice.first)
        second_image_id = self.__read_image_id(choice.second)
        self.cursor.execute('''INSERT INTO choices (provided_at, answered_at, first, second) VALUES (?, ?, ?, ?)''',
                            (choice.provided, choice.answered, first_image_id, second_image_id))
        self.con.commit()

    def __read_image_id(self, filename):
        self.cursor.execute('SELECT id FROM images WHERE filename = ?', (filename,))
        return self.cursor.fetchone()[0]

    def get_random_image(self) -> (int, str):
        # if self.number_images == 0:
        #     self.cursor.execute('SELECT count(id) FROM images WHERE id > 0')
        #     self.number_images: int = self.cursor.fetchone()[0]
        # random_int_1 = random.randint(1, self.number_images)
        # random_int_2 = random.randint(1, self.number_images)
        # if random_int_1 == random_int_2:
        #     random_int_2 = random_int_2 + 1
        # self.cursor.execute('SELECT id, filename FROM images WHERE id >= ? AND id <= ? + 10', (random_int_1,))
        self.cursor.execute('SELECT id, filename FROM images ORDER BY RANDOM() LIMIT 10')
        return self.cursor.fetchone()[0]
