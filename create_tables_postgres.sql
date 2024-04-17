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
    url VARCHAR(1000) NOT NULL,
    skip BOOLEAN DEFAULT FALSE,
    downloaded BOOLEAN DEFAULT FALSE
);
CREATE UNIQUE INDEX idx_links_url ON links(url);
CREATE TABLE documents_to_links (
    id SERIAL PRIMARY KEY,
    document_id INTEGER NOT NULL,
    link_id INTEGER NOT NULL,
    CONSTRAINT fk_document FOREIGN KEY (document_id) REFERENCES documents(id),
    CONSTRAINT fk_link FOREIGN KEY (link_id) REFERENCES links(id)
);
CREATE UNIQUE INDEX idx_documents_links on documents_to_links(document_id, link_id);
CREATE TABLE images (
    id SERIAL PRIMARY KEY,
    url VARCHAR(1000) NOT NULL,
    filename VARCHAR(1000),
    size INTEGER,
    width INTEGER,
    height INTEGER,
    skip BOOLEAN DEFAULT FALSE,
    downloaded BOOLEAN DEFAULT FALSE
);
CREATE UNIQUE INDEX idx_images_url ON images(url);
CREATE TABLE documents_to_images (
    id SERIAL PRIMARY KEY,
    document_id INTEGER NOT NULL,
    image_id INTEGER NOT NULL,
    CONSTRAINT fk_document FOREIGN KEY (document_id) REFERENCES documents(id),
    CONSTRAINT fk_image FOREIGN KEY (image_id) REFERENCES images(id)
);
CREATE UNIQUE INDEX idx_documents_images on documents_to_images(document_id, image_id);
