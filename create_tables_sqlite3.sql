CREATE TABLE documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url VARCHAR(1000) NOT NULL,
    content TEXT NOT NULL,
    downloaded_at DATETIME NOT NULL,
    created_at DATETIME,
    created_by VARCHAR(100)
);
CREATE TABLE links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL,
    url VARCHAR(1000) NOT NULL
);
CREATE TABLE images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL,
    url VARCHAR(1000) NOT NULL,
    filename VARCHAR(1000),
    size INTEGER,
    width INTEGER,
    height INTEGER
);
