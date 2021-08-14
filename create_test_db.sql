-- Database: train_excel_test
DROP TABLE public.headers;
DROP TABLE public.sentence;
DROP TABLE public.token_label;
DROP TABLE public.sentence_label;
DROP TABLE public."users";


CREATE TABLE public."users"
(
    id SERIAL NOT NULL,
    name character varying(64),
    PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE public."users"
    OWNER to postgres;



CREATE TABLE public.headers
(
    id SERIAL NOT NULL,
    text character varying(512) NOT NULL,
    column_num integer NOT NULL,
    target_num integer NOT NULL,
    user_id integer NOT NULL,
	subset_id integer NOT NULL,
    PRIMARY KEY (id),
	CONSTRAINT fk_column
   FOREIGN KEY(user_id) 
   REFERENCES users(id)
)

TABLESPACE pg_default;

ALTER TABLE public.headers
    OWNER to postgres;



CREATE TABLE public.sentence_label
(
    id SERIAL NOT NULL,
    category character varying(128) NOT NULL,
    ordinal character varying(16) NOT NULL UNIQUE,
    PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE public.sentence_label
    OWNER to postgres;



CREATE TABLE public.token_label
(
    id SERIAL NOT NULL,
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
    id SERIAL NOT NULL,
    text character varying(1024) NOT NULL,
    label integer NOT NULL,
    token_labels integer[],
    PRIMARY KEY (id),
    CONSTRAINT fk_label
   FOREIGN KEY(label) 
   REFERENCES sentence_label(id)
)

TABLESPACE pg_default;

ALTER TABLE public.sentence
    OWNER to postgres;
    