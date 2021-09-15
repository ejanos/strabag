-- Database: train_excel_test

-- DROP DATABASE train_excel_test

DROP TABLE public.headers;
DROP TABLE public.sentence;
DROP TABLE public.token_label;
DROP TABLE public.sentence_label;
DROP TABLE public.architects;


CREATE TABLE public."architects"
(
    id SERIAL NOT NULL,
    name character varying(64) NOT NULL,
    created_date date DEFAULT CURRENT_DATE,
    modified_date date DEFAULT CURRENT_DATE,
    active boolean DEFAULT true,
    PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE public."architects"
    OWNER to postgres;



CREATE TABLE public.headers
(
    id SERIAL NOT NULL,
    text character varying(512) NOT NULL,
    column_num integer NOT NULL,
    target_num integer NOT NULL,
    architect_id integer NOT NULL,
	subset_id integer NOT NULL,
	header_row integer NOT NULL,
    PRIMARY KEY (id),
	CONSTRAINT fk_column
   FOREIGN KEY(architect_id) 
   REFERENCES architects(id)
)

TABLESPACE pg_default;

ALTER TABLE public.headers
    OWNER to postgres;



CREATE TABLE public.sentence_label
(
    id SERIAL NOT NULL,
    category character varying(128) NOT NULL,
    ordinal character varying(16) NOT NULL UNIQUE,
    created_date date DEFAULT CURRENT_DATE,
    modified_date date DEFAULT CURRENT_DATE,
	type_identity integer NOT NULL,
	main_cat_id integer NOT NULL,
	sub_cat_id integer NOT NULL,
	category_order DEFAULT 0,
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
    created_date date DEFAULT CURRENT_DATE,
    modified_date date DEFAULT CURRENT_DATE,
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
    sentence_label_id integer NOT NULL,
    token_labels integer[],
	result_id integer NOT NULL,
	user_identity integer NOT NULL,
    PRIMARY KEY (id),
    CONSTRAINT fk_label
   FOREIGN KEY(sentence_label_id) 
   REFERENCES sentence_label(id)
)

TABLESPACE pg_default;

ALTER TABLE public.sentence
    OWNER to postgres;
    
