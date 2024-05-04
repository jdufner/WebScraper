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
    url VARCHAR(1000) NOT NULL
);
CREATE TABLE documents_to_links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL,
    link_ID INTEGER NOT NULL
);
CREATE TABLE images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url VARCHAR(1000) NOT NULL,
    filename VARCHAR(1000),
    size INTEGER,
    width INTEGER,
    height INTEGER
);
CREATE TABLE documents_to_images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL,
    image_id INTEGER NOT NULL
);
CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100)
);
CREATE TABLE documents_to_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL,
    category_id INTEGER NOT NULL
);
