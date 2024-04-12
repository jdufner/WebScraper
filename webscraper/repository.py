from datetime import datetime
import sqlite3
from webscraper.document import Document


class Repository:
    def __init__(self) -> None:
        self.con = sqlite3.connect(':memory:')
        self.cursor = self.con.cursor()

    def __del__(self) -> None:
        self.con.close()

    def create_tables(self):
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
            document_id INTEGER NOT NULL,
            url VARCHAR(1000) NOT NULL
        )''')
        self.cursor.execute('''CREATE TABLE images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id INTEGER NOT NULL,
            url VARCHAR(1000) NOT NULL,
            filename VARCHAR(1000),
            size INTEGER,
            width INTEGER,
            height INTEGER
        )''')
        # now = datetime.now()
        # self.cursor.executemany('INSERT INTO documents (url, content, downloaded_at) VALUES '
        #                         '(:url, :content, :downloaded_at)', (
        #                             {'url': 'http://www.heise.de/', 'content': '<html></html>', 'downloaded_at': now},
        #                             {'url': 'http://www.heise.de/ct', 'content': '<html></html>', 'downloaded_at': now}
        #                         ))
        # cur = self.cursor.execute('SELECT * from documents')
        # print(cur.fetchall())

    def save_document(self, document: Document):
        self.cursor.execute('INSERT INTO documents (url, content, downloaded_at, created_at, created_by) VALUES'
                            '(?, ?, ?, ?, ?)',
                            (document.url, document.content, document.downloaded_at, document.created_ad[0],
                             document.creators[0]))
        document_id: int = self.cursor.lastrowid
        self.cursor.executemany('INSERT INTO links (document_id, url) VALUES (:document_id, :url)',
                                self.__list_to_link_dict(document, document_id))
        self.cursor.executemany('INSERT INTO images (document_id, url) VALUES (:document_id, :url)',
                                self.__list_to_link_dict(document, document_id))

    def get_all(self):
        cur = self.cursor.execute('SELECT * FROM documents d, links l, images i WHERE d.id = l.document_id and d.id = '
                                  'i.document_id')
        print(cur.fetchall())

    @staticmethod
    def __list_to_link_dict(document: Document, document_id: int) -> list[dict]:
        list_of_dicts: list[dict] = []
        for link in document.links:
            list_of_dicts.append({'document_id': document_id, 'url': link})
        return list_of_dicts

    @staticmethod
    def __document_to_images_dict(document: Document, document_id: int) -> list[dict]:
        list_of_dicts: list[dict] = []
        for image_url in document.image_urls:
            list_of_dicts.append({'document_id': document_id, 'url': image_url})
        return list_of_dicts


if __name__ == '__main__':
    r = Repository()
    r.create_tables()
    d = Document('https://www.heise.de/', '<html>..</html>', datetime.now(),
                 [str(datetime.now())], ['Michael Schmitt'], ['https://www.heise.de/ct', 'https://www.heise.de/ix'],
                 ['https://www.heise.de/pic.jpg'])
    r.save_document(d)
    r.get_all()
