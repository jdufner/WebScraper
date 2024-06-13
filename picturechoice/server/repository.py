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

    @abstractmethod
    def get_total_number_images(self):
        pass

    @abstractmethod
    def get_number_not_yet_rated_images(self):
        pass

    @abstractmethod
    def get_not_yet_rated_image_by_row_num(self, row_num):
        pass

    @abstractmethod
    def set_image_as_rated_by(self, id):
        pass

    @abstractmethod
    def get_number_already_rated_images(self):
        pass

    @abstractmethod
    def get_already_rated_image_by_row_num(self, row_num):
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
        # first_image_id = self.__read_image_id(choice.first)
        # second_image_id = self.__read_image_id(choice.second)
        self.cursor.execute('INSERT INTO choices (provided_at, answered_at, first, second) VALUES (?, ?, ?, ?)',
                            (choice.provided, choice.answered, choice.first, choice.second))
        # self.cursor.execute('UPDATE images SET rank = rank + 1 WHERE id = ?', (first_image_id, ))
        # self.cursor.execute('UPDATE images SET rank = rank - 1 WHERE id = ?', (second_image_id, ))
        self.cursor.execute('UPDATE images SET rank = rank + 1 WHERE id = ?', (choice.first, ))
        self.cursor.execute('UPDATE images SET rank = rank - 1 WHERE id = ?', (choice.second, ))
        self.con.commit()

    def __read_image_id(self, filename) -> int:
        self.cursor.execute('SELECT id FROM images WHERE filename = ?', (filename,))
        return self.cursor.fetchone()[0]

    def get_random_image(self) -> (int, str):
        self.cursor.execute('SELECT id, filename FROM images WHERE downloaded = 1 ORDER BY RANDOM() LIMIT 10')
        return self.cursor.fetchone()[0], self.cursor.fetchone()[1]

    def get_total_number_images(self) -> int:
        self.cursor.execute('SELECT count(id) FROM images WHERE downloaded = 1')
        return self.cursor.fetchone()[0]

    def get_number_not_yet_rated_images(self) -> int:
        self.cursor.execute('SELECT count(id) FROM images WHERE downloaded = 1 AND rank = -1000')
        return self.cursor.fetchone()[0]

    def get_not_yet_rated_image_by_row_num(self, row_num) -> (int, str):
        print(f'row_num = {row_num}')
        self.cursor.execute('SELECT id, filename FROM '
                            '(SELECT row_number() OVER (ORDER BY id) AS row_num, id, filename '
                            'FROM images '
                            'WHERE downloaded = 1 AND rank = -1000) '
                            'WHERE row_num = ?', (row_num, ))
        row = self.cursor.fetchone()
        print(f'row = {row}')
        return row[0], row[1]

    def set_image_as_rated_by(self, id) -> None:
        self.cursor.execute('UPDATE images SET rank = 0 WHERE id = ?', (id, ))
        self.con.commit()

    def get_number_already_rated_images(self):
        self.cursor.execute('SELECT count(id) FROM images WHERE rank > -1000')
        return self.cursor.fetchone()[0]

    def get_already_rated_image_by_row_num(self, row_num):
        print(f'row_num = {row_num}')
        self.cursor.execute('SELECT id, filename FROM '
                            '(SELECT row_number() OVER (order by rank) AS row_num, id, filename '
                            'FROM images '
                            'WHERE downloaded = 1 AND rank > -1000) '
                            'WHERE row_num = ?', (row_num, ))
        row = self.cursor.fetchone()
        print(f'row = {row}')
        return row[0], row[1]
