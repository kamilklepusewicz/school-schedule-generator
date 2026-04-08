--
-- PostgreSQL database dump
--

\restrict WwwY0kdf0FhJ4RudkaibcZaA8kIFQudAg4eVcvNOdcEVls8Ub4d60wgbBKkkA6P

-- Dumped from database version 18.3
-- Dumped by pg_dump version 18.3

-- Started on 2026-03-29 10:06:42

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
-- TOC entry 222 (class 1259 OID 16498)
-- Name: classroom; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.classroom (
    id integer NOT NULL,
    number character varying(20) NOT NULL,
    name character varying(100),
    seats_count integer NOT NULL,
    classroom_type_id integer NOT NULL
);


ALTER TABLE public.classroom OWNER TO postgres;

--
-- TOC entry 221 (class 1259 OID 16497)
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

--
-- TOC entry 5065 (class 0 OID 0)
-- Dependencies: 221
-- Name: classroom_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.classroom_id_seq OWNED BY public.classroom.id;


--
-- TOC entry 220 (class 1259 OID 16489)
-- Name: classroom_type; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.classroom_type (
    id integer NOT NULL,
    name character varying(100) NOT NULL
);


ALTER TABLE public.classroom_type OWNER TO postgres;

--
-- TOC entry 219 (class 1259 OID 16488)
-- Name: classroom_type_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.classroom_type_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.classroom_type_id_seq OWNER TO postgres;

--
-- TOC entry 5066 (class 0 OID 0)
-- Dependencies: 219
-- Name: classroom_type_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.classroom_type_id_seq OWNED BY public.classroom_type.id;


--
-- TOC entry 230 (class 1259 OID 16548)
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
    status character varying(20)
);


ALTER TABLE public.lesson OWNER TO postgres;

--
-- TOC entry 229 (class 1259 OID 16547)
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

--
-- TOC entry 5067 (class 0 OID 0)
-- Dependencies: 229
-- Name: lesson_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.lesson_id_seq OWNED BY public.lesson.id;


--
-- TOC entry 228 (class 1259 OID 16539)
-- Name: student_group; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.student_group (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    student_count integer,
    year smallint
);


ALTER TABLE public.student_group OWNER TO postgres;

--
-- TOC entry 227 (class 1259 OID 16538)
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

--
-- TOC entry 5068 (class 0 OID 0)
-- Dependencies: 227
-- Name: student_group_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.student_group_id_seq OWNED BY public.student_group.id;


--
-- TOC entry 226 (class 1259 OID 16524)
-- Name: subject; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.subject (
    id integer NOT NULL,
    name character varying(150) NOT NULL,
    classroom_type_id integer NOT NULL
);


ALTER TABLE public.subject OWNER TO postgres;

--
-- TOC entry 225 (class 1259 OID 16523)
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

--
-- TOC entry 5069 (class 0 OID 0)
-- Dependencies: 225
-- Name: subject_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.subject_id_seq OWNED BY public.subject.id;


--
-- TOC entry 224 (class 1259 OID 16514)
-- Name: teacher; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.teacher (
    id integer NOT NULL,
    first_name character varying(100) NOT NULL,
    last_name character varying(100) NOT NULL
);


ALTER TABLE public.teacher OWNER TO postgres;

--
-- TOC entry 223 (class 1259 OID 16513)
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

--
-- TOC entry 5070 (class 0 OID 0)
-- Dependencies: 223
-- Name: teacher_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.teacher_id_seq OWNED BY public.teacher.id;


--
-- TOC entry 231 (class 1259 OID 16583)
-- Name: teacher_subject; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.teacher_subject (
    teacher_id integer NOT NULL,
    subject_id integer NOT NULL
);


ALTER TABLE public.teacher_subject OWNER TO postgres;

--
-- TOC entry 4886 (class 2604 OID 16501)
-- Name: classroom id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.classroom ALTER COLUMN id SET DEFAULT nextval('public.classroom_id_seq'::regclass);


--
-- TOC entry 4885 (class 2604 OID 16492)
-- Name: classroom_type id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.classroom_type ALTER COLUMN id SET DEFAULT nextval('public.classroom_type_id_seq'::regclass);


--
-- TOC entry 4890 (class 2604 OID 16551)
-- Name: lesson id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.lesson ALTER COLUMN id SET DEFAULT nextval('public.lesson_id_seq'::regclass);


--
-- TOC entry 4889 (class 2604 OID 16542)
-- Name: student_group id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.student_group ALTER COLUMN id SET DEFAULT nextval('public.student_group_id_seq'::regclass);


--
-- TOC entry 4888 (class 2604 OID 16527)
-- Name: subject id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.subject ALTER COLUMN id SET DEFAULT nextval('public.subject_id_seq'::regclass);


--
-- TOC entry 4887 (class 2604 OID 16517)
-- Name: teacher id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.teacher ALTER COLUMN id SET DEFAULT nextval('public.teacher_id_seq'::regclass);


--
-- TOC entry 4894 (class 2606 OID 16507)
-- Name: classroom classroom_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.classroom
    ADD CONSTRAINT classroom_pkey PRIMARY KEY (id);


--
-- TOC entry 4892 (class 2606 OID 16496)
-- Name: classroom_type classroom_type_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.classroom_type
    ADD CONSTRAINT classroom_type_pkey PRIMARY KEY (id);


--
-- TOC entry 4902 (class 2606 OID 16562)
-- Name: lesson lesson_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.lesson
    ADD CONSTRAINT lesson_pkey PRIMARY KEY (id);


--
-- TOC entry 4900 (class 2606 OID 16546)
-- Name: student_group student_group_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.student_group
    ADD CONSTRAINT student_group_pkey PRIMARY KEY (id);


--
-- TOC entry 4898 (class 2606 OID 16532)
-- Name: subject subject_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.subject
    ADD CONSTRAINT subject_pkey PRIMARY KEY (id);


--
-- TOC entry 4896 (class 2606 OID 16522)
-- Name: teacher teacher_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.teacher
    ADD CONSTRAINT teacher_pkey PRIMARY KEY (id);


--
-- TOC entry 4904 (class 2606 OID 16589)
-- Name: teacher_subject teacher_subject_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.teacher_subject
    ADD CONSTRAINT teacher_subject_pkey PRIMARY KEY (teacher_id, subject_id);


--
-- TOC entry 4905 (class 2606 OID 16508)
-- Name: classroom classroom_classroom_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.classroom
    ADD CONSTRAINT classroom_classroom_type_id_fkey FOREIGN KEY (classroom_type_id) REFERENCES public.classroom_type(id);


--
-- TOC entry 4907 (class 2606 OID 16568)
-- Name: lesson lesson_classroom_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.lesson
    ADD CONSTRAINT lesson_classroom_id_fkey FOREIGN KEY (classroom_id) REFERENCES public.classroom(id);


--
-- TOC entry 4908 (class 2606 OID 16578)
-- Name: lesson lesson_group_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.lesson
    ADD CONSTRAINT lesson_group_id_fkey FOREIGN KEY (group_id) REFERENCES public.student_group(id);


--
-- TOC entry 4909 (class 2606 OID 16563)
-- Name: lesson lesson_subject_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.lesson
    ADD CONSTRAINT lesson_subject_id_fkey FOREIGN KEY (subject_id) REFERENCES public.subject(id);


--
-- TOC entry 4910 (class 2606 OID 16573)
-- Name: lesson lesson_teacher_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.lesson
    ADD CONSTRAINT lesson_teacher_id_fkey FOREIGN KEY (teacher_id) REFERENCES public.teacher(id);


--
-- TOC entry 4906 (class 2606 OID 16533)
-- Name: subject subject_classroom_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.subject
    ADD CONSTRAINT subject_classroom_type_id_fkey FOREIGN KEY (classroom_type_id) REFERENCES public.classroom_type(id);


--
-- TOC entry 4911 (class 2606 OID 16595)
-- Name: teacher_subject teacher_subject_subject_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.teacher_subject
    ADD CONSTRAINT teacher_subject_subject_id_fkey FOREIGN KEY (subject_id) REFERENCES public.subject(id);


--
-- TOC entry 4912 (class 2606 OID 16590)
-- Name: teacher_subject teacher_subject_teacher_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.teacher_subject
    ADD CONSTRAINT teacher_subject_teacher_id_fkey FOREIGN KEY (teacher_id) REFERENCES public.teacher(id);


-- Completed on 2026-03-29 10:06:42

--
-- PostgreSQL database dump complete
--

\unrestrict WwwY0kdf0FhJ4RudkaibcZaA8kIFQudAg4eVcvNOdcEVls8Ub4d60wgbBKkkA6P

