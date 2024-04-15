DROP TABLE images;
DROP TABLE links;
DROP TABLE documents;
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    url VARCHAR(1000) NOT NULL,
    content TEXT NOT NULL,
    downloaded_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE,
    created_by VARCHAR(100)
);
CREATE TABLE links (
    id SERIAL PRIMARY KEY,
    document_id INTEGER NOT NULL,
    url VARCHAR(1000) NOT NULL,
    CONSTRAINT fk_document FOREIGN KEY (document_id) REFERENCES documents(id)
);
CREATE TABLE images (
    id SERIAL PRIMARY KEY,
    document_id INTEGER NOT NULL,
    url VARCHAR(1000) NOT NULL,
    filename VARCHAR(1000),
    size INTEGER,
    width INTEGER,
    height INTEGER,
    CONSTRAINT fk_document FOREIGN KEY (document_id) REFERENCES documents(id)
);
