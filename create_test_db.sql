-- Database: merkbau_test

-- DROP DATABASE merkbau_test;

DROP TABLE IF EXISTS public.sentence;
DROP TABLE IF EXISTS public.token_label;
DROP TABLE IF EXISTS public.sentence_label;
DROP TABLE IF EXISTS public.headers;
DROP TABLE IF EXISTS public.PandasArchitect;


DROP TABLE IF EXISTS public.sentence;
DROP TABLE IF EXISTS public.token_label;
DROP TABLE IF EXISTS public.sentence_label;
DROP TABLE IF EXISTS public.headers;
DROP TABLE IF EXISTS public.PandasArchitect;


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
	TypeId integer NOT NULL,
	MainCatId integer NOT NULL,
	SubCatId integer NOT NULL,
	CategoryOrder integer DEFAULT 0,
    PRIMARY KEY (PandasCategoryId)
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
   REFERENCES sentence_label(PandasCategoryId)
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
	PandasResultId integer REFERENCES PandasResult,
	UserId integer REFERENCES Users,
    PRIMARY KEY (id),
    CONSTRAINT fk_label
   FOREIGN KEY(sentence_label_id)
   REFERENCES sentence_label(PandasCategoryId)
)

TABLESPACE pg_default;

ALTER TABLE public.sentence
    OWNER to postgres;
