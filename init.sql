--
-- Modified PostgreSQL database dump (init.sql)
--

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';
SET default_table_access_method = heap;

--
-- Name: classroom; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.classroom (
    id integer NOT NULL,
    name character varying(100)
);

ALTER TABLE public.classroom OWNER TO postgres;

--
-- Name: classroom_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.classroom_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE public.classroom_id_seq OWNER TO postgres;
ALTER SEQUENCE public.classroom_id_seq OWNED BY public.classroom.id;

--
-- Name: lesson; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.lesson (
    id integer NOT NULL,
    subject_id integer NOT NULL,
    classroom_id integer NOT NULL,
    teacher_id integer NOT NULL,
    group_id integer NOT NULL,
    start_time timestamp without time zone NOT NULL,
    end_time timestamp without time zone NOT NULL,
    description text,
    --status character varying(20)
);

ALTER TABLE public.lesson OWNER TO postgres;

--
-- Name: lesson_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.lesson_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE public.lesson_id_seq OWNER TO postgres;
ALTER SEQUENCE public.lesson_id_seq OWNED BY public.lesson.id;

--
-- Name: student_group; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.student_group (
    id integer NOT NULL,
    name character varying(100) NOT NULL
);

ALTER TABLE public.student_group OWNER TO postgres;

--
-- Name: student_group_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.student_group_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE public.student_group_id_seq OWNER TO postgres;
ALTER SEQUENCE public.student_group_id_seq OWNED BY public.student_group.id;

--
-- Name: subject; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.subject (
    id integer NOT NULL,
    name character varying(150) NOT NULL
);

ALTER TABLE public.subject OWNER TO postgres;

--
-- Name: subject_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.subject_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE public.subject_id_seq OWNER TO postgres;
ALTER SEQUENCE public.subject_id_seq OWNED BY public.subject.id;

--
-- Name: teacher; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.teacher (
    id integer NOT NULL,
    first_name character varying(100) NOT NULL,
    last_name character varying(100) NOT NULL,
    subject_id integer
);

ALTER TABLE public.teacher OWNER TO postgres;

--
-- Name: teacher_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.teacher_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE public.teacher_id_seq OWNER TO postgres;
ALTER SEQUENCE public.teacher_id_seq OWNED BY public.teacher.id;

--
-- Setting Defaults for IDs
--

ALTER TABLE ONLY public.classroom ALTER COLUMN id SET DEFAULT nextval('public.classroom_id_seq'::regclass);
ALTER TABLE ONLY public.lesson ALTER COLUMN id SET DEFAULT nextval('public.lesson_id_seq'::regclass);
ALTER TABLE ONLY public.student_group ALTER COLUMN id SET DEFAULT nextval('public.student_group_id_seq'::regclass);
ALTER TABLE ONLY public.subject ALTER COLUMN id SET DEFAULT nextval('public.subject_id_seq'::regclass);
ALTER TABLE ONLY public.teacher ALTER COLUMN id SET DEFAULT nextval('public.teacher_id_seq'::regclass);

--
-- Primary Keys
--

ALTER TABLE ONLY public.classroom ADD CONSTRAINT classroom_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.lesson ADD CONSTRAINT lesson_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.student_group ADD CONSTRAINT student_group_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.subject ADD CONSTRAINT subject_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.teacher ADD CONSTRAINT teacher_pkey PRIMARY KEY (id);

--
-- Foreign Keys
--

ALTER TABLE ONLY public.lesson
    ADD CONSTRAINT lesson_classroom_id_fkey FOREIGN KEY (classroom_id) REFERENCES public.classroom(id);

ALTER TABLE ONLY public.lesson
    ADD CONSTRAINT lesson_group_id_fkey FOREIGN KEY (group_id) REFERENCES public.student_group(id);

ALTER TABLE ONLY public.lesson
    ADD CONSTRAINT lesson_subject_id_fkey FOREIGN KEY (subject_id) REFERENCES public.subject(id);

ALTER TABLE ONLY public.lesson
    ADD CONSTRAINT lesson_teacher_id_fkey FOREIGN KEY (teacher_id) REFERENCES public.teacher(id);

ALTER TABLE ONLY public.teacher
    ADD CONSTRAINT teacher_subject_id_fkey FOREIGN KEY (subject_id) REFERENCES public.subject(id);
