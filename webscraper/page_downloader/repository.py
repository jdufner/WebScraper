from abc import abstractmethod
import psycopg
import re
import sqlite3
from webscraper.page_downloader.document import Document


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
    def save_document(self, document: Document) -> None:
        pass

    def save_document_content_as_per_config(self, document: Document) -> str | None:
        if self.config["download"]["save-html"].lower() == 'true':
            return document.content
        else:
            return ''

    @abstractmethod
    def get_next_link(self) -> tuple[int, str]:
        pass

    @abstractmethod
    def set_link_downloaded(self, link_url: str) -> None:
        pass

    @abstractmethod
    def set_link_skip(self, link_id: int) -> None:
        pass

    @abstractmethod
    def get_next_image_url(self) -> tuple[int, str]:
        pass

    @abstractmethod
    def set_image_downloaded(self, image_id: int) -> None:
        pass

    @abstractmethod
    def set_image_skip(self, image_id: int) -> None:
        pass

    @abstractmethod
    def update_image(self, image_id, filename, size, image_width, image_height) -> None:
        pass

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
    def __init__(self, config: dict) -> None:
        super().__init__(config)
        if self.config["database"]["type"].lower() == "in-memory":
            self.con = sqlite3.connect(self.config["database"]["in-memory"]["url"])
        else:
            self.con = sqlite3.connect(self.config["database"]["sqlite3"]["url"])
        self.cursor = self.con.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url VARCHAR(1000) NOT NULL,
            content TEXT,
            title TEXT,
            downloaded_at DATETIME NOT NULL,
            created_at DATETIME,
            created_by VARCHAR(100)
        )''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS links (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url VARCHAR(1000) NOT NULL UNIQUE,
            skip INTEGER DEFAULT 0,
            downloaded INTEGER DEFAULT 0
        )''')
        self.cursor.execute('''CREATE UNIQUE INDEX IF NOT EXISTS idx_links ON links(url)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS documents_to_links (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id INTEGER NOT NULL,
            link_id INTEGER NOT NULL
        )''')
        self.cursor.execute('''CREATE UNIQUE INDEX IF NOT EXISTS idx_documents_links ON 
                            documents_to_links(document_id, link_id)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url VARCHAR(1000) NOT NULL UNIQUE,
            size_folder INTEGER,
            filename VARCHAR(1000),
            filesize INTEGER,
            width INTEGER,
            height INTEGER,
            skip INTEGER DEFAULT 0,
            downloaded INTEGER DEFAULT 0
        )''')
        self.cursor.execute('''CREATE UNIQUE INDEX IF NOT EXISTS idx_images_url ON images(url)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS documents_to_images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id INTEGER NOT NULL,
            image_id INTEGER NOT NULL
        )''')
        self.cursor.execute('''CREATE UNIQUE INDEX IF NOT EXISTS idx_documents_images ON 
                            documents_to_images(document_id, image_id)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) NOT NULL UNIQUE
        )''')
        self.cursor.execute('''CREATE UNIQUE INDEX IF NOT EXISTS idx_categories_name ON categories(name)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS documents_to_categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id INTEGER NOT NULL,
            category_id INTEGER NOT NULL
        )''')
        self.cursor.execute('''CREATE UNIQUE INDEX IF NOT EXISTS idx_documents_categories ON
                            documents_to_categories(document_id, category_id)''')

    def save_document(self, document: Document) -> None:
        self.cursor.execute('INSERT INTO documents (url, content, title, downloaded_at, created_at, created_by) '
                            'VALUES (?, ?, ?, ?, ?, ?)',
                            (document.url, self.save_document_content_as_per_config(document),
                             document.title, document.downloaded_at, document.created_at_or_none(),
                             document.created_by_as_string()))
        document_id: int = self.cursor.lastrowid
        self.__save_links(document, document_id)
        self.__save_image_urls(document, document_id)
        self.__save_categories(document, document_id)
        self.con.commit()

    def __save_links(self, document, document_id):
        for link in list(dict.fromkeys(document.links)):
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

    def __save_image_urls(self, document, document_id):
        for image_url in list(dict.fromkeys(document.image_urls)):
            self.cursor.execute('SELECT id FROM images WHERE url = ?', (image_url,))
            result = self.cursor.fetchone()
            image_id: int
            if result is None:
                self.cursor.execute('INSERT INTO images (url, size_folder) VALUES (?, ?)',
                                    (image_url, self.__extract_size_folder(image_url)))
                image_id = self.cursor.lastrowid
            else:
                image_id = result[0]
            self.cursor.execute('INSERT INTO documents_to_images (document_id, image_id) VALUES (?, ?)',
                                (document_id, image_id))

    def __save_categories(self, document, document_id):
        for category in list(dict.fromkeys(document.categories)):
            self.cursor.execute('SELECT id FROM categories WHERE name = ?', (category,))
            result = self.cursor.fetchone()
            category_id: int
            if result is None:
                self.cursor.execute('INSERT INTO categories (name) VALUES (?)', (category,))
                category_id = self.cursor.lastrowid
            else:
                category_id = result[0]
            self.cursor.execute('INSERT INTO documents_to_categories (document_id, category_id) VALUES (?, ?)',
                                (document_id, category_id))

    def __extract_size_folder(self, url) -> int | None:
        match = re.search('https?://(\\w+.\\w+.\\w+)/(\\d+)/', url)
        if match is not None:
            return int(match.group(2))

    def get_next_link(self) -> tuple[int, str]:
        self.cursor.execute('''SELECT l.id, l.url FROM links l LEFT OUTER JOIN documents d ON l.url = d.url 
                            WHERE d.id IS NULL AND l.downloaded = 0 AND l.skip = 0 ORDER BY l.id ASC''')
        result = self.cursor.fetchone()
        return int(result[0]), str(result[1])

    def set_link_downloaded(self, link_url: str) -> None:
        self.cursor.execute('UPDATE links SET downloaded = 1 WHERE url = ?', (link_url,))
        self.con.commit()

    def set_link_skip(self, link_id: int) -> None:
        self.cursor.execute('UPDATE links SET skip = 1 WHERE id = ?', (link_id,))
        self.con.commit()

    def get_next_image_url(self) -> tuple[int, str]:
        self.cursor.execute('SELECT i.id, i.url FROM images i WHERE i.downloaded = 0 AND i.skip = 0 ORDER BY i.id ASC')
        result = self.cursor.fetchone()
        return int(result[0]), str(result[1])

    def set_image_downloaded(self, image_id: int) -> None:
        self.cursor.execute('UPDATE images SET downloaded = 1 WHERE id = ?', (image_id,))
        self.con.commit()

    def set_image_skip(self, image_id: int) -> None:
        self.cursor.execute('UPDATE images SET skip = 1 WHERE id = ?', (image_id,))
        self.con.commit()

    def update_image(self, image_id, filename, size, image_width, image_height) -> None:
        self.cursor.execute('UPDATE images SET filename = ?, filesize = ?, width = ?, height = ? WHERE id = ?',
                            (filename, size, image_width, image_height, image_id))
        self.con.commit()


class PostgresqlRepository(Repository):
    def __init__(self, config: dict) -> None:
        super().__init__(config)
        self.con = psycopg.connect(dbname=(self.config["database"]["postgres"]["url"]),
                                   user=(self.config["database"]["postgres"]["username"]),
                                   password=(self.config["database"]["postgres"]["password"]))
        self.cursor = self.con.cursor()

    def create_tables(self) -> None:
        pass

    def save_document(self, document: Document) -> None:
        self.cursor.execute('INSERT INTO documents (url, content, downloaded_at, created_at, created_by) VALUES'
                            '(%s, %s, %s, %s, %s) RETURNING id',
                            (document.url, document.title, document.downloaded_at, document.created_at_or_none(),
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

    def get_next_link(self) -> tuple[int, str]:
        self.cursor.execute('''SELECT l.id, l.url FROM links l LEFT OUTER JOIN documents d ON l.url = d.url 
                            WHERE d.id IS NULL AND (l.downloaded = FALSE OR l.downloaded IS NULL) AND 
                            (l.skip = FALSE OR l.skip IS NULL) ORDER BY l.id ASC''')
        result = self.cursor.fetchone()
        return int(result[0]), str(result[1])

    def set_link_downloaded(self, link_url: str) -> None:
        self.cursor.execute('UPDATE links SET downloaded = TRUE WHERE url = %s', (link_url,))
        self.con.commit()

    def set_link_skip(self, link_id: int) -> None:
        self.cursor.execute('UPDATE links SET skip = TRUE WHERE id = %s', (link_id,))
        self.con.commit()

    def get_next_image_url(self) -> tuple[int, str]:
        self.cursor.execute('''SELECT i.id, i.url FROM images i WHERE (i.downloaded = FALSE OR i.downloaded IS NULL) AND 
                            (i.skip = FALSE or i.skip IS NULL) ORDER BY i.id ASC''')
        result = self.cursor.fetchone()
        return int(result[0]), str(result[1])

    def set_image_downloaded(self, image_id: int) -> None:
        self.cursor.execute('UPDATE images SET downloaded = TRUE WHERE id = %s', (image_id,))
        self.con.commit()

    def set_image_skip(self, image_id: int) -> None:
        self.cursor.execute('UPDATE images SET skip = TRUE WHERE id = %s', (image_id,))
        self.con.commit()

    def update_image(self, image_id, filename, size, image_width, image_height) -> None:
        self.cursor.execute('UPDATE images SET filename = %s, size = %s, width = %s, height = %s WHERE id = %s',
                            (filename, size, image_width, image_height, image_id))
        self.con.commit()
