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

DROP TABLE IF EXISTS public.architects;
CREATE TABLE public."architects"
(
    architect_id SERIAL NOT NULL,
    name character varying(64) NOT NULL,
    created_date date DEFAULT CURRENT_DATE,
    modified_date date DEFAULT CURRENT_DATE,
    active boolean DEFAULT true,
    PRIMARY KEY (architect_id)
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
   REFERENCES architects(architect_id)
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
	type_id integer NOT NULL,
	main_cat_id integer NOT NULL,
	sub_cat_id integer NOT NULL,
	category_order integer DEFAULT 0,
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
	user_id integer NOT NULL,
    PRIMARY KEY (id),
    CONSTRAINT fk_label
   FOREIGN KEY(sentence_label_id) 
   REFERENCES sentence_label(id)
)

TABLESPACE pg_default;

ALTER TABLE public.sentence
    OWNER to postgres;

CREATE TABLE public.pandas_result
(
    pandas_result_id SERIAL NOT NULL,
    project_id integer,
    file_id integer,
    result_name character varying(128) NOT NULL,
    result_count integer,
    result_finish integer,
    result_table integer[][],
    PRIMARY KEY (pandas_result_id)
)

TABLESPACE pg_default;

ALTER TABLE public.pandas_result
    OWNER to postgres;

CREATE TABLE public.pandas_column
(
    pandas_column_id SERIAL NOT NULL,
    project_id integer,
    result_id integer REFERENCES pandas_result,
    architect_id integer REFERENCES architects,
    content_value integer,
    content_text character varying(256),
    quantity_value integer,
    quantity_text character varying(256),
    unit_value integer,
    unit_text character varying(256),
    material_value integer,
    material_text character varying(256),
    wage_value integer,
    wage_text character varying(256),
    sum_value integer,
    sum_text character varying(256),
    created_date date DEFAULT CURRENT_DATE,
    column_row json NOT NULL,
    PRIMARY KEY (pandas_column_id)
)

TABLESPACE pg_default;

ALTER TABLE public.pandas_column
    OWNER to postgres;


    
