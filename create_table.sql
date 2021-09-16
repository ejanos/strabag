-- Database: merkbau

-- DROP DATABASE merkbau;

CREATE DATABASE merkbau
    WITH
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'hu_HU.UTF-8'
    LC_CTYPE = 'hu_HU.UTF-8'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1;


DROP TABLE IF EXISTS public.PandasColumn;
DROP TABLE IF EXISTS public.PandasResult;
DROP TABLE IF EXISTS public.PandasFile;
DROP TABLE IF EXISTS public.PandasProject;
DROP TABLE IF EXISTS public.sentence;
DROP TABLE IF EXISTS public.token_label;
DROP TABLE IF EXISTS public.sentence_label;
DROP TABLE IF EXISTS public.headers;
DROP TABLE IF EXISTS public.PandasArchitect;
DROP TABLE IF EXISTS public.Users;


CREATE TABLE public.Users
(
    UserId SERIAL NOT NULL,
    FirstName character varying(128),
    LastName character varying(128),
    Email character varying(128),
    Password character varying(128),
    CreatedAt date DEFAULT CURRENT_DATE,
    Active boolean DEFAULT true,
    Confirmed boolean DEFAULT false,
    ExpireAt date DEFAULT CURRENT_DATE,
    PRIMARY KEY (UserId)
)

TABLESPACE pg_default;

ALTER TABLE public.Users
    OWNER to postgres;


CREATE TABLE public.PandasArchitect
(
    PandasArchitectId SERIAL NOT NULL,
    ArchitectName character varying(64) NOT NULL,
    CreateDate date DEFAULT CURRENT_DATE,
    ModifiedDate date DEFAULT CURRENT_DATE,
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

CREATE TABLE public.PandasProject
(
    PandasProjectId SERIAL NOT NULL,
	UserId integer REFERENCES Users,
	PandasArchitectId integer REFERENCES PandasArchitect,
	PandasProjectName character varying(256) NOT NULL,
	CreateDate date DEFAULT CURRENT_DATE,
	ModifyDate date DEFAULT CURRENT_DATE,
	Active boolean DEFAULT true,
    PRIMARY KEY (PandasProjectId)
)

TABLESPACE pg_default;

ALTER TABLE public.PandasProject
    OWNER to postgres;

CREATE TABLE public.PandasFile
(
    PandasFileId SERIAL NOT NULL,
	PandasProjectId integer REFERENCES PandasProject,
	FileName character varying(256) NOT NULL,
	FileSize integer NOT NULL,
	FileType character varying(128) NOT NULL,
	FileData bytea,
    PRIMARY KEY (PandasFileId)
)

TABLESPACE pg_default;

ALTER TABLE public.PandasFile
    OWNER to postgres;


CREATE TABLE public.PandasResult
(
    PandasResultId SERIAL NOT NULL,
    PandasProjectId integer,
    PandasFileId integer,
    ResultName character varying(128) NOT NULL,
    ResultCount integer,
    ResultFinish integer,
    ResultTable integer[][],
    PRIMARY KEY (PandasResultId)
)

TABLESPACE pg_default;

ALTER TABLE public.PandasResult
    OWNER to postgres;


CREATE TABLE public.PandasColumn
(
    PandasColumnId SERIAL NOT NULL,
    PandasProjectId integer,
    PandasResultId integer REFERENCES PandasResult,
    PandasArchitectId integer REFERENCES PandasArchitect,
    ContentValue integer,
    ContentText character varying(256),
    QuantityValue integer,
    QuantityText character varying(256),
    UnitValue integer,
    UnitText character varying(256),
    MaterialValue integer,
    MaterialText character varying(256),
    WageValue integer,
    WageText character varying(256),
    SumValue integer,
    SumText character varying(256),
    CreateDate date DEFAULT CURRENT_DATE,
    ColumnRow json NOT NULL,
    PRIMARY KEY (PandasColumnId)
)

TABLESPACE pg_default;

ALTER TABLE public.PandasColumn
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
