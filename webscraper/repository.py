from _datetime import datetime
import sqlite3


class Repository:
    def __init__(self) -> None:
        self.con = sqlite3.connect(':memory:')
        self.cursor = self.con.cursor()

    def __del__(self) -> None:
        self.con.close()

    def create_tables(self):
        now = datetime.now()
        self.cursor.execute('''CREATE TABLE documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url VARCHAR(1000) NOT NULL,
            content TEXT NOT NULL,
            downloaded_at DATETIME NOT NULL,
            created_at DATETIME,
            created_by VARCHAR(100)
        )''')
        self.cursor.executemany('INSERT INTO documents (url, content, downloaded_at) VALUES '
                                '(:url, :content, :downloaded_at)', (
                                    {'url': 'http://www.heise.de/', 'content': '<html></html>', 'downloaded_at': now},
                                    {'url': 'http://www.heise.de/ct', 'content': '<html></html>', 'downloaded_at': now}
                                ))
        cur = self.cursor.execute('SELECT * from documents')
        print(cur.fetchall())


if __name__ == '__main__':
    Repository().create_tables()
