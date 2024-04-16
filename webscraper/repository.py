from abc import abstractmethod
from datetime import datetime
import json
import psycopg
import sqlite3
from webscraper.document import Document


class Repository:
    def __init__(self, config: dict) -> None:
        self.config = config
        self.con = None
        self.cursor = None

    def __del__(self) -> None:
        self.con.close()

    @abstractmethod
    def create_tables(self):
        pass

    @abstractmethod
    def save_document(self, document: Document):
        pass

    def get_all(self):
        cur = self.cursor.execute('SELECT * FROM documents d, documents_to_links dl, links l, documents_to_images di, '
                                  'images i WHERE d.id = dl.document_id and dl.link_id = l.id and '
                                  'd.id = di.document_id and di.image_id = i.id')
        print(cur.fetchall())

    @staticmethod
    def document_to_link_dict(document: Document, document_id: int) -> list[dict]:
        list_of_dicts: list[dict] = []
        for link in document.links:
            list_of_dicts.append({'document_id': document_id, 'url': link})
        return list_of_dicts

    @staticmethod
    def document_to_link_list(document: Document, document_id: int) -> list[tuple]:
        list_of_tuples: list[tuple] = []
        for link in document.links:
            list_of_tuples.append((document_id, link))
        return list_of_tuples

    @staticmethod
    def document_to_images_dict(document: Document, document_id: int) -> list[dict]:
        list_of_dicts: list[dict] = []
        for image_url in document.image_urls:
            list_of_dicts.append({'document_id': document_id, 'url': image_url})
        return list_of_dicts

    @staticmethod
    def document_to_images_list(document: Document, document_id: int) -> list[tuple]:
        list_of_tuples: list[tuple] = []
        for image_url in document.image_urls:
            list_of_tuples.append((document_id, image_url))
        return list_of_tuples


class SqliteRepository(Repository):
    def __init__(self, config: dict):
        super().__init__(config)
        self.con = sqlite3.connect(self.config["database"]["url"])
        self.cursor = self.con.cursor()
        self.create_tables()

    def create_tables(self):
        # self.cursor.execute('''DROP TABLE images''')
        # self.cursor.execute('''DROP TABLE links''')
        # self.cursor.execute('''DROP TABLE documents''')
        self.cursor.execute('''CREATE TABLE documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url VARCHAR(1000) NOT NULL,
            content TEXT NOT NULL,
            downloaded_at DATETIME NOT NULL,
            created_at DATETIME,
            created_by VARCHAR(100)
        )''')
        self.cursor.execute('''CREATE TABLE links (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url VARCHAR(1000) NOT NULL
        )''')
        self.cursor.execute('''CREATE TABLE documents_to_links (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id INTEGER NOT NULL,
            link_ID INTEGER NOT NULL
        )''')
        self.cursor.execute('''CREATE TABLE images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url VARCHAR(1000) NOT NULL,
            filename VARCHAR(1000),
            size INTEGER,
            width INTEGER,
            height INTEGER
        )''')
        self.cursor.execute('''CREATE TABLE documents_to_images (
           id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id INTEGER NOT NULL,
            image_id INTEGER NOT NULL
        )''')

    def save_document(self, document: Document):
        self.cursor.execute('INSERT INTO documents (url, content, downloaded_at, created_at, created_by) VALUES'
                            '(?, ?, ?, ?, ?)',
                            (document.url, document.content, document.downloaded_at,
                             document.created_at_or_none(), document.created_by_as_string()))
        document_id: int = self.cursor.lastrowid
        for link in document.links:
            self.cursor.execute('SELECT id FROM links WHERE url = ?', (link,))
            result = self.cursor.fetchone()
            link_id: int
            if result is None:
                self.cursor.execute('INSERT INTO links (url) VALUES (?)', (link,))
                link_id = self.cursor.lastrowid
            else:
                link_id = result[0]
            self.cursor.execute('INSERT INTO documents_to_links (document_id, link_id) values (?, ?)',
                                (document_id, link_id))
        for image_url in document.image_urls:
            self.cursor.execute('SELECT id from images WHERE url = ?', (image_url,))
            result = self.cursor.fetchone()
            image_id: int
            if result is None:
                self.cursor.execute('INSERT INTO images (url) VALUES (?)', (image_url,))
                image_id = self.cursor.lastrowid
            else:
                image_id = result[0]
            self.cursor.execute('INSERT INTO documents_to_images (document_id, image_id) VALUES (?, ?)',
                                (document_id, image_id))


class PostgresqlRepository(Repository):
    def __init__(self, config: dict):
        super().__init__(config)
        self.con = psycopg.connect(dbname=(self.config["database"]["url"]),
                                   user=(self.config["database"]["username"]),
                                   password=(self.config["database"]["password"]))
        self.cursor = self.con.cursor()

    def create_tables(self):
        self.cursor.execute('''CREATE TABLE documents (
            id SERIAL PRIMARY KEY,
            url VARCHAR(1000) NOT NULL,
            content TEXT NOT NULL,
            downloaded_at TIMESTAMP WITH TIME ZONE NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE,
            created_by VARCHAR(100)
        )''')
        self.cursor.execute('''CREATE TABLE links (
            id SERIAL PRIMARY KEY,
            document_id INTEGER NOT NULL,
            url VARCHAR(1000) NOT NULL,
            CONSTRAINT fk_document FOREIGN KEY (document_id) REFERENCES documents(id)
        )''')
        self.cursor.execute('''CREATE TABLE images (
            id SERIAL PRIMARY KEY,
            document_id INTEGER NOT NULL,
            url VARCHAR(1000) NOT NULL,
            filename VARCHAR(1000),
            size INTEGER,
            width INTEGER,
            height INTEGER,
            CONSTRAINT fk_document FOREIGN KEY (document_id) REFERENCES documents(id)
        )''')

    def save_document(self, document: Document):
        self.cursor.execute('INSERT INTO documents (url, content, downloaded_at, created_at, created_by) VALUES'
                            '(%s, %s, %s, %s, %s) RETURNING id',
                            (document.url, document.content, document.downloaded_at, document.created_at_or_none(),
                             document.created_by_as_string()))
        document_id: int = self.cursor.fetchone()[0]
        for link in list(dict.fromkeys(document.links)):
            self.cursor.execute('SELECT id FROM links WHERE url = %s', (link,))
            result = self.cursor.fetchone()
            link_id: int
            if result is None:
                self.cursor.execute('INSERT INTO links (url) VALUES (%s) RETURNING id', (link,))
                link_id = self.cursor.fetchone()[0]
            else:
                link_id = result[0]
            self.cursor.execute('INSERT INTO documents_to_links (document_id, link_id) values (%s, %s)',
                                (document_id, link_id))
        for image_url in list(dict.fromkeys(document.image_urls)):
            self.cursor.execute('SELECT id from images WHERE url = %s', (image_url,))
            result = self.cursor.fetchone()
            image_id: int
            if result is None:
                self.cursor.execute('INSERT INTO images (url) VALUES (%s) RETURNING id', (image_url,))
                image_id = self.cursor.fetchone()[0]
            else:
                image_id = result[0]
            self.cursor.execute('INSERT INTO documents_to_images (document_id, image_id) VALUES (%s, %s)',
                                (document_id, image_id))
        self.con.commit()


def init_sqlite() -> Repository:
    config = json.load(open('../config-heise.json'))
    r: Repository = SqliteRepository(config)
    return r


def init_postgresql() -> Repository:
    config = json.load(open('../config-heise.json'))
    r: Repository = PostgresqlRepository(config)
    return r


if __name__ == '__main__':
    # r = init_sqlite()
    r = init_postgresql()
    d = Document('https://www.heise.de/', '<html>..</html>', datetime.now(),
                 [str(datetime.now())], ['Michael Schmitt'],
                 ['https://www.heise.de/ct', 'https://www.heise.de/ix', 'https://www.heise.de/ct'],
                 ['https://www.heise.de/pic.jpg'])
    r.save_document(d)
    r.get_all()

    # timestamp: float = time.time()
    # print(timestamp)
    # dt: datetime = datetime.fromtimestamp(timestamp)
    # print(dt)
