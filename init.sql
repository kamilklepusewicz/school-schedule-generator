--
-- PostgreSQL database dump
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
-- Name: classroom_type; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.classroom_type (
    id SERIAL PRIMARY KEY,
    name character varying(100) NOT NULL
);

ALTER TABLE public.classroom_type OWNER TO postgres;

--
-- Name: classroom; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.classroom (
    id SERIAL PRIMARY KEY,
    name character varying(100),
    classroom_type_id integer NOT NULL
);

ALTER TABLE public.classroom OWNER TO postgres;

--
-- Name: subject; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.subject (
    id SERIAL PRIMARY KEY,
    name character varying(150) NOT NULL,
    classroom_type_id integer NOT NULL
);

ALTER TABLE public.subject OWNER TO postgres;

--
-- Name: teacher; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.teacher (
    id SERIAL PRIMARY KEY,
    first_name character varying(100) NOT NULL,
    last_name character varying(100) NOT NULL,
    subject_id integer
);

ALTER TABLE public.teacher OWNER TO postgres;

--
-- Name: student_group; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.student_group (
    id SERIAL PRIMARY KEY,
    name character varying(100) NOT NULL
);

ALTER TABLE public.student_group OWNER TO postgres;

--
-- Name: lesson_count; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.lesson_count (
    student_group_id integer NOT NULL,
    subject_id integer NOT NULL,
    hours integer NOT NULL,
    PRIMARY KEY (student_group_id, subject_id)
);

ALTER TABLE public.lesson_count OWNER TO postgres;

--
-- Name: lesson; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.lesson (
    id SERIAL PRIMARY KEY,
    subject_id integer NOT NULL,
    classroom_id integer NOT NULL,
    teacher_id integer NOT NULL,
    group_id integer NOT NULL,
    day integer NOT NULL,
    start integer NOT NULL
);

ALTER TABLE public.lesson OWNER TO postgres;

--
-- Constraints (Klucze obce)
--

ALTER TABLE ONLY public.classroom
    ADD CONSTRAINT classroom_classroom_type_id_fkey FOREIGN KEY (classroom_type_id) REFERENCES public.classroom_type(id);

ALTER TABLE ONLY public.subject
    ADD CONSTRAINT subject_classroom_type_id_fkey FOREIGN KEY (classroom_type_id) REFERENCES public.classroom_type(id);

ALTER TABLE ONLY public.teacher
    ADD CONSTRAINT teacher_subject_id_fkey FOREIGN KEY (subject_id) REFERENCES public.subject(id);

ALTER TABLE ONLY public.lesson_count
    ADD CONSTRAINT lesson_count_student_group_id_fkey FOREIGN KEY (student_group_id) REFERENCES public.student_group(id);

ALTER TABLE ONLY public.lesson_count
    ADD CONSTRAINT lesson_count_subject_id_fkey FOREIGN KEY (subject_id) REFERENCES public.subject(id);

ALTER TABLE ONLY public.lesson
    ADD CONSTRAINT lesson_subject_id_fkey FOREIGN KEY (subject_id) REFERENCES public.subject(id);

ALTER TABLE ONLY public.lesson
    ADD CONSTRAINT lesson_classroom_id_fkey FOREIGN KEY (classroom_id) REFERENCES public.classroom(id);

ALTER TABLE ONLY public.lesson
    ADD CONSTRAINT lesson_teacher_id_fkey FOREIGN KEY (teacher_id) REFERENCES public.teacher(id);

ALTER TABLE ONLY public.lesson
    ADD CONSTRAINT lesson_group_id_fkey FOREIGN KEY (group_id) REFERENCES public.student_group(id);
