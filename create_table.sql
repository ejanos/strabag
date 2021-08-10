-- Database: train_excel

-- DROP DATABASE train_excel;

CREATE DATABASE train_excel
    WITH 
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'Hungarian_Hungary.1250'
    LC_CTYPE = 'Hungarian_Hungary.1250'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1;

CREATE TABLE public.sentence_label
(
    category character varying(128) NOT NULL,
    id integer NOT NULL,
    ordinal character varying(16) NOT NULL,
    PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE public.sentence_label
    OWNER to postgres;
    
CREATE TABLE public.token_label
(
    id integer NOT NULL,
    name character varying(128) NOT NULL,
    category_id integer,
    PRIMARY KEY (id),
    CONSTRAINT fk_token_label
   FOREIGN KEY(category_id) 
   REFERENCES sentence_label(id)
)

TABLESPACE pg_default;

ALTER TABLE public.token_label
    OWNER to postgres;

CREATE TABLE public.sentence
(
    text character varying(1024) NOT NULL,
    label integer,
    id integer NOT NULL,
    token_labels integer[],
    PRIMARY KEY (id),
    CONSTRAINT fk_label
   FOREIGN KEY(label) 
   REFERENCES sentence_label(id)
)

TABLESPACE pg_default;

ALTER TABLE public.sentence
    OWNER to postgres;
    
