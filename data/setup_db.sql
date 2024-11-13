
-- INSTALL POSTGRES
-- On mac installed using Postgress.App (version 16)
-- Add to ~/.zshrc export PATH=$PATH:/Applications/Postgres.app/Contents/Versions/latest/bin

--  INSTALL PGVECTOR
-- cd /tmp
-- git clone --branch v0.4.1 https://github.com/pgvector/pgvector.git
-- cd pgvector
-- make
-- make install

-- INSTALL PGVECTORSCALE (Version 0.4.0)
-- Instructions here - https://github.com/timescale/pgvectorscale?tab=readme-ov-file#installing-from-source
-- FAILED (Try again later)

-- psql -U postgres
-- CREATE USER scrapy WITH PASSWORD #### 
-- CREATE USER admin WITH PASSWORD ####
-- CREATE DATABASE wingman;
-- GRANT CONNECT ON DATABASE wingman TO admin;
-- GRANT CONNECT ON DATABASE wingman TO scrapy;
-- psql -U postgres -d wingman
-- GRANT SELECT, INSERT ON ALL TABLES IN SCHEMA public TO scrapy;
-- GRANT ALL PRIVILEGES ON SCHEMA public TO admin;

-- enable pgvector
CREATE EXTENSION IF NOT EXISTS vector;
-- install pgvector scale
-- CREATE EXTENSION IF NOT EXISTS vectorscale CASCADE;

-- create Tables
CREATE TABLE retailer (
    id bigserial primary key,
    name VARCHAR(255)
);

CREATE TABLE retailer_pages (
    id bigserial primary key,
    retailer_id INT,
    FOREIGN KEY (retailer_id) REFERENCES retailer(id),
    url VARCHAR,
    title VARCHAR,
    html text,
    description text,
    -- Think about splitting this out in a separate table later on.
    images text
);

CREATE TABLE retailer_pages_embeddings (
    id bigserial primary key,
    retailer_id INT,
    FOREIGN KEY (retailer_id) REFERENCES retailer(id),
    -- ID specific to a URL
    text_id VARCHAR(127),
    url VARCHAR,
    text VARCHAR,
    embedding vector(1536)

);

-- To run post insertion of data
--CREATE INDEX ON retailer_pages_embeddings USING ivfflat (embedding vector_ip_ops);
--CREATE INDEX ON retailer_pages_embeddings USING ivfflat (embedding vector_l2_ops);
