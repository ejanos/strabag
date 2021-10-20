-- Database: merkbau

-- DROP DATABASE merkbau;

CREATE DATABASE omegavision
    WITH
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'hu_HU.UTF-8'
    LC_CTYPE = 'hu_HU.UTF-8'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1;


DROP TABLE IF EXISTS public.sentence;
DROP TABLE IF EXISTS public.token_label;
DROP TABLE IF EXISTS public.sentence_label;
DROP TABLE IF EXISTS public.headers;
DROP TABLE IF EXISTS public.PandasArchitect;
DROP TABLE IF EXISTS public.TrainedProjects;


CREATE TABLE public.TrainedProjects
(
    TrainedProjectId integer PRIMARY KEY NOT NULL,
    Trained boolean
)

TABLESPACE pg_default;

ALTER TABLE public.TrainedProjects
    OWNER to postgres;

CREATE TABLE public.PandasArchitect
(
    PandasArchitectId SERIAL NOT NULL,
    ArchitectName character varying(64) NOT NULL,
    CreateDate date DEFAULT CURRENT_DATE,
    ModifyDate date DEFAULT CURRENT_DATE,
    Active boolean DEFAULT true,
    PRIMARY KEY (PandasArchitectId)
)

TABLESPACE pg_default;

ALTER TABLE public.PandasArchitect
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
   REFERENCES PandasArchitect(PandasArchitectId)
)

TABLESPACE pg_default;

ALTER TABLE public.headers
    OWNER to postgres;

CREATE TABLE public.sentence_label
(
    PandasCategoryId SERIAL NOT NULL,
    CategoryName character varying(128) NOT NULL,
    Ordinal character varying(16) NOT NULL UNIQUE,
    CreateDate date DEFAULT CURRENT_DATE,
    ModifiedDate date DEFAULT CURRENT_DATE,
    PRIMARY KEY (PandasCategoryId)
)

TABLESPACE pg_default;

ALTER TABLE public.sentence_label
    OWNER to postgres;

CREATE TABLE public.token_label
(
    id SERIAL NOT NULL,
    frontend_id integer NOT NULL,
    name character varying(128) NOT NULL UNIQUE,
    category_id integer,
    created_date date DEFAULT CURRENT_DATE,
    modified_date date DEFAULT CURRENT_DATE,
    PRIMARY KEY (id),
    CONSTRAINT fk_token_label
   FOREIGN KEY(category_id)
   REFERENCES sentence_label(PandasCategoryId)
)

TABLESPACE pg_default;

ALTER TABLE public.token_label
    OWNER to postgres;

CREATE TABLE public.sentence
(
    id SERIAL NOT NULL,
    text character varying(1024) NOT NULL UNIQUE,
    sentence_label_id integer NOT NULL,
    token_labels integer[],
    PRIMARY KEY (id),
    CONSTRAINT fk_label
   FOREIGN KEY(sentence_label_id)
   REFERENCES sentence_label(PandasCategoryId)
)

TABLESPACE pg_default;

ALTER TABLE public.sentence
    OWNER to postgres;
