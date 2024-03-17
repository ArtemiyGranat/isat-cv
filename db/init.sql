CREATE DATABASE isat_cv_db;
\c isat_cv_db

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";

CREATE TABLE images (
    id uuid DEFAULT uuid_generate_v4(),
    url varchar(512) UNIQUE NOT NULL,
    hash varchar(128) UNIQUE NOT NULL,
    hsv float[3],
    lab float[3],
    image_embeddings vector,
    text_embeddings vector,
    processed boolean NOT NULL,

    PRIMARY KEY(id)
)
