--
-- PostgreSQL database dump
--

-- Dumped from database version 11.4
-- Dumped by pg_dump version 11.4

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: goals; Type: TABLE; Schema: public; Owner: courtneyholcomb
--

CREATE TABLE public.goals (
    id integer NOT NULL,
    user_id integer,
    habit_id integer,
    num_units double precision NOT NULL,
    time_period interval NOT NULL
);


ALTER TABLE public.goals OWNER TO courtneyholcomb;

--
-- Name: goals_id_seq; Type: SEQUENCE; Schema: public; Owner: courtneyholcomb
--

CREATE SEQUENCE public.goals_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.goals_id_seq OWNER TO courtneyholcomb;

--
-- Name: goals_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: courtneyholcomb
--

ALTER SEQUENCE public.goals_id_seq OWNED BY public.goals.id;


--
-- Name: habit_events; Type: TABLE; Schema: public; Owner: courtneyholcomb
--

CREATE TABLE public.habit_events (
    id integer NOT NULL,
    user_id integer,
    habit_id integer,
    num_units double precision,
    "timestamp" timestamp without time zone NOT NULL,
    latitude double precision,
    longitude double precision
);


ALTER TABLE public.habit_events OWNER TO courtneyholcomb;

--
-- Name: habit_events_id_seq; Type: SEQUENCE; Schema: public; Owner: courtneyholcomb
--

CREATE SEQUENCE public.habit_events_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.habit_events_id_seq OWNER TO courtneyholcomb;

--
-- Name: habit_events_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: courtneyholcomb
--

ALTER SEQUENCE public.habit_events_id_seq OWNED BY public.habit_events.id;


--
-- Name: habits; Type: TABLE; Schema: public; Owner: courtneyholcomb
--

CREATE TABLE public.habits (
    id integer NOT NULL,
    user_id integer,
    label character varying(30) NOT NULL,
    unit character varying(20)
);


ALTER TABLE public.habits OWNER TO courtneyholcomb;

--
-- Name: habits_id_seq; Type: SEQUENCE; Schema: public; Owner: courtneyholcomb
--

CREATE SEQUENCE public.habits_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.habits_id_seq OWNER TO courtneyholcomb;

--
-- Name: habits_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: courtneyholcomb
--

ALTER SEQUENCE public.habits_id_seq OWNED BY public.habits.id;


--
-- Name: influence_events; Type: TABLE; Schema: public; Owner: courtneyholcomb
--

CREATE TABLE public.influence_events (
    id integer NOT NULL,
    user_id integer,
    influence_id integer,
    intensity integer,
    "timestamp" timestamp without time zone NOT NULL,
    latitude double precision,
    longitude double precision
);


ALTER TABLE public.influence_events OWNER TO courtneyholcomb;

--
-- Name: influence_events_id_seq; Type: SEQUENCE; Schema: public; Owner: courtneyholcomb
--

CREATE SEQUENCE public.influence_events_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.influence_events_id_seq OWNER TO courtneyholcomb;

--
-- Name: influence_events_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: courtneyholcomb
--

ALTER SEQUENCE public.influence_events_id_seq OWNED BY public.influence_events.id;


--
-- Name: influences; Type: TABLE; Schema: public; Owner: courtneyholcomb
--

CREATE TABLE public.influences (
    id integer NOT NULL,
    user_id integer,
    label character varying(30) NOT NULL,
    scale character varying(20)
);


ALTER TABLE public.influences OWNER TO courtneyholcomb;

--
-- Name: influences_id_seq; Type: SEQUENCE; Schema: public; Owner: courtneyholcomb
--

CREATE SEQUENCE public.influences_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.influences_id_seq OWNER TO courtneyholcomb;

--
-- Name: influences_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: courtneyholcomb
--

ALTER SEQUENCE public.influences_id_seq OWNED BY public.influences.id;


--
-- Name: symptom_events; Type: TABLE; Schema: public; Owner: courtneyholcomb
--

CREATE TABLE public.symptom_events (
    id integer NOT NULL,
    user_id integer,
    symptom_id integer,
    intensity integer,
    "timestamp" timestamp without time zone NOT NULL,
    latitude double precision,
    longitude double precision
);


ALTER TABLE public.symptom_events OWNER TO courtneyholcomb;

--
-- Name: symptom_events_id_seq; Type: SEQUENCE; Schema: public; Owner: courtneyholcomb
--

CREATE SEQUENCE public.symptom_events_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.symptom_events_id_seq OWNER TO courtneyholcomb;

--
-- Name: symptom_events_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: courtneyholcomb
--

ALTER SEQUENCE public.symptom_events_id_seq OWNED BY public.symptom_events.id;


--
-- Name: symptoms; Type: TABLE; Schema: public; Owner: courtneyholcomb
--

CREATE TABLE public.symptoms (
    id integer NOT NULL,
    user_id integer,
    label character varying(50) NOT NULL,
    scale character varying(20)
);


ALTER TABLE public.symptoms OWNER TO courtneyholcomb;

--
-- Name: symptoms_id_seq; Type: SEQUENCE; Schema: public; Owner: courtneyholcomb
--

CREATE SEQUENCE public.symptoms_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.symptoms_id_seq OWNER TO courtneyholcomb;

--
-- Name: symptoms_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: courtneyholcomb
--

ALTER SEQUENCE public.symptoms_id_seq OWNED BY public.symptoms.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: courtneyholcomb
--

CREATE TABLE public.users (
    id integer NOT NULL,
    email character varying(64) NOT NULL,
    username character varying(25) NOT NULL,
    password character varying(64) NOT NULL,
    gcal_token bytea
);


ALTER TABLE public.users OWNER TO courtneyholcomb;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: courtneyholcomb
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.users_id_seq OWNER TO courtneyholcomb;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: courtneyholcomb
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: goals id; Type: DEFAULT; Schema: public; Owner: courtneyholcomb
--

ALTER TABLE ONLY public.goals ALTER COLUMN id SET DEFAULT nextval('public.goals_id_seq'::regclass);


--
-- Name: habit_events id; Type: DEFAULT; Schema: public; Owner: courtneyholcomb
--

ALTER TABLE ONLY public.habit_events ALTER COLUMN id SET DEFAULT nextval('public.habit_events_id_seq'::regclass);


--
-- Name: habits id; Type: DEFAULT; Schema: public; Owner: courtneyholcomb
--

ALTER TABLE ONLY public.habits ALTER COLUMN id SET DEFAULT nextval('public.habits_id_seq'::regclass);


--
-- Name: influence_events id; Type: DEFAULT; Schema: public; Owner: courtneyholcomb
--

ALTER TABLE ONLY public.influence_events ALTER COLUMN id SET DEFAULT nextval('public.influence_events_id_seq'::regclass);


--
-- Name: influences id; Type: DEFAULT; Schema: public; Owner: courtneyholcomb
--

ALTER TABLE ONLY public.influences ALTER COLUMN id SET DEFAULT nextval('public.influences_id_seq'::regclass);


--
-- Name: symptom_events id; Type: DEFAULT; Schema: public; Owner: courtneyholcomb
--

ALTER TABLE ONLY public.symptom_events ALTER COLUMN id SET DEFAULT nextval('public.symptom_events_id_seq'::regclass);


--
-- Name: symptoms id; Type: DEFAULT; Schema: public; Owner: courtneyholcomb
--

ALTER TABLE ONLY public.symptoms ALTER COLUMN id SET DEFAULT nextval('public.symptoms_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: courtneyholcomb
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: goals; Type: TABLE DATA; Schema: public; Owner: courtneyholcomb
--

COPY public.goals (id, user_id, habit_id, num_units, time_period) FROM stdin;
\.


--
-- Data for Name: habit_events; Type: TABLE DATA; Schema: public; Owner: courtneyholcomb
--

COPY public.habit_events (id, user_id, habit_id, num_units, "timestamp", latitude, longitude) FROM stdin;
1	1	1	1	2019-08-18 03:00:00	\N	\N
2	1	1	1	2019-08-19 18:30:00	\N	\N
3	1	1	1	2019-08-19 20:00:00	\N	\N
4	1	1	1	2019-08-20 15:00:00	\N	\N
5	1	1	1	2019-08-21 18:15:00	\N	\N
11	1	1	3	2019-08-23 13:06:57.675809	37.7887594999999976	-122.411530399999975
13	1	1	5	2019-08-23 15:23:40.976656	37.7887485999999981	-122.411522200000007
15	1	1	2	2019-08-26 11:28:05.774948	37.7887336000000005	-122.411545799999999
16	1	1	2	2019-08-26 11:52:46.50821	37.7887303999999986	-122.411559499999996
17	1	1	1	2019-08-25 09:00:00	\N	\N
19	1	1	1	2019-08-25 10:00:00	\N	\N
20	1	1	1	2019-08-26 18:30:00	\N	\N
34	4	15	30	2019-09-07 15:35:16.633718	\N	\N
35	4	15	20	2019-09-07 15:44:01.116161	\N	\N
36	4	15	1	2019-09-02 12:00:00	\N	\N
37	4	15	1	2019-09-07 11:30:00	\N	\N
40	1	1	1	2019-09-07 11:30:00	\N	\N
41	1	1	1	2019-09-08 16:30:00	\N	\N
45	1	1	1	2019-09-09 18:30:00	\N	\N
46	1	1	1	2019-09-10 18:15:00	\N	\N
47	1	4	1	2019-09-12 06:30:00	\N	\N
48	1	1	1	2019-09-14 16:30:00	\N	\N
49	1	1	1	2019-09-10 12:00:00	\N	\N
50	1	1	4	2019-09-11 13:34:36.197409	\N	\N
51	1	1	5	2019-09-11 13:35:39.819541	\N	\N
52	1	1	1	2019-09-13 12:00:00	37.7887387999999973	-122.411508799999979
53	6	19	1	2019-09-07 11:30:00	\N	\N
54	6	19	1	2019-09-08 16:30:00	\N	\N
55	6	19	1	2019-09-09 18:30:00	\N	\N
56	6	19	1	2019-09-10 18:15:00	\N	\N
58	1	1	2	2019-09-13 12:41:22.198487	37.7887661999999978	-122.41170910000001
59	1	1	1	2019-09-13 12:45:28.613883	37.7887298999999999	-122.411523199999976
60	1	1	1	2019-09-13 12:00:00	37.7887387999999973	-122.411512300000012
61	1	1	10	2019-09-13 15:35:42.49729	37.7887197999999955	-122.411559700000012
62	1	1	20	2019-09-13 16:23:05.101858	37.7886791999999971	-122.41152910000001
63	1	1	15	2019-09-13 16:25:51.854338	\N	\N
64	1	5	1	2019-09-12 12:00:00	\N	\N
65	1	4	1	2019-09-12 13:00:00	\N	\N
66	1	1	1	2019-09-12 15:00:00	\N	\N
67	1	4	1	2019-09-10 12:00:00	\N	\N
68	1	1	1	2019-09-10 13:00:00	\N	\N
70	1	5	1	2019-09-11 12:00:00	\N	\N
72	1	5	1	2019-09-11 15:00:00	\N	\N
73	1	4	1	2019-09-11 16:00:00	\N	\N
74	1	5	1	2019-09-12 16:00:00	\N	\N
76	1	4	1	2019-09-11 18:00:00	\N	\N
77	1	1	10	2019-09-16 12:00:00	37.7887349999999955	-122.411528599999997
78	1	1	1	2019-09-15 16:30:00	\N	\N
79	1	1	20	2019-09-16 12:00:00	37.7887142999999952	-122.411531299999979
80	1	3	1	2019-09-04 20:00:00	\N	\N
83	1	4	1	2019-09-18 09:00:00	\N	\N
84	1	4	1	2019-09-19 07:00:00	\N	\N
85	1	4	1	2019-09-20 07:00:00	\N	\N
86	1	1	1	2019-09-28 16:30:00	\N	\N
87	1	3	3	2019-09-03 12:00:00	\N	\N
88	1	3	4	2019-09-03 14:00:00	\N	\N
89	1	3	5	2019-09-03 17:00:00	\N	\N
100	1	1	2	2019-09-17 12:00:00	37.7493452000000005	-122.415798299999992
101	1	3	1	2019-09-12 22:00:00	\N	\N
102	1	4	1	2019-09-14 15:00:00	\N	\N
103	1	4	1	2019-09-15 13:00:00	\N	\N
104	1	1	1	2019-09-16 18:00:00	\N	\N
105	1	1	1	2019-09-17 19:00:00	\N	\N
106	1	1	1	2019-09-17 20:00:00	\N	\N
\.


--
-- Data for Name: habits; Type: TABLE DATA; Schema: public; Owner: courtneyholcomb
--

COPY public.habits (id, user_id, label, unit) FROM stdin;
1	1	yoga	hours
3	1	drink	drinks
4	1	climb	hours
5	1	meditate	minutes
8	1	smoke	cigarettes
15	4	yoga	asanas
18	1	sleep early	nights
19	6	yoga	asanas
20	6	meditate	minutes
26	1	run	miles
\.


--
-- Data for Name: influence_events; Type: TABLE DATA; Schema: public; Owner: courtneyholcomb
--

COPY public.influence_events (id, user_id, influence_id, intensity, "timestamp", latitude, longitude) FROM stdin;
1	1	1	71	2019-08-23 13:06:57.85907	37.7887594999999976	-122.411530399999975
2	1	2	800	2019-08-23 13:06:57.85907	37.7887594999999976	-122.411530399999975
3	1	1	71	2019-08-23 15:23:41.262647	37.7887485999999981	-122.411522200000007
4	1	2	804	2019-08-23 15:23:41.262647	37.7887485999999981	-122.411522200000007
5	1	1	75	2019-08-26 11:26:54.298178	37.7887336000000005	-122.411545799999999
6	1	2	801	2019-08-26 11:26:54.298178	37.7887336000000005	-122.411545799999999
7	1	1	75	2019-08-26 11:28:05.973759	37.7887336000000005	-122.411545799999999
8	1	2	801	2019-08-26 11:28:05.973759	37.7887336000000005	-122.411545799999999
9	1	1	76	2019-08-26 11:52:46.853401	37.7887303999999986	-122.411559499999996
10	1	2	800	2019-08-26 11:52:46.853401	37.7887303999999986	-122.411559499999996
11	1	1	61	2019-08-26 22:56:53.044203	37.757778799999997	-122.413635099999993
12	1	2	741	2019-08-26 22:56:53.044203	37.757778799999997	-122.413635099999993
13	1	1	70	2019-08-28 13:33:37.047042	37.7887437999999989	-122.411541599999993
14	1	2	803	2019-08-28 13:33:37.047042	37.7887437999999989	-122.411541599999993
15	1	3	10	2019-08-28 13:33:36.775342	37.7887437999999989	-122.411541599999993
16	1	3	10	2019-08-28 13:33:55.888555	\N	\N
17	1	1	70	2019-08-28 13:34:18.828435	37.7887437999999989	-122.411541599999993
18	1	2	803	2019-08-28 13:34:18.828435	37.7887437999999989	-122.411541599999993
19	1	3	7	2019-08-28 13:34:18.632464	37.7887437999999989	-122.411541599999993
20	2	1	72	2019-08-30 12:49:26.980204	37.7886814000000015	-122.411554199999998
21	2	2	802	2019-08-30 12:49:26.980204	37.7886814000000015	-122.411554199999998
22	4	1	67	2019-09-07 15:43:33.18767	37.7493511999999996	-122.415811399999981
23	4	2	804	2019-09-07 15:43:33.18767	37.7493511999999996	-122.415811399999981
24	4	1	67	2019-09-07 15:52:06.164003	37.7493571999999986	-122.415827199999995
25	4	2	804	2019-09-07 15:52:06.164003	37.7493571999999986	-122.415827199999995
26	4	1	67	2019-09-07 15:53:04.510182	37.7493571999999986	-122.415827199999995
27	4	2	804	2019-09-07 15:53:04.510182	37.7493571999999986	-122.415827199999995
28	4	1	67	2019-09-07 15:55:50.819503	37.7493550999999954	-122.415810500000006
29	4	2	804	2019-09-07 15:55:50.819503	37.7493550999999954	-122.415810500000006
30	4	1	67	2019-09-07 16:00:52.712263	37.7493440000000007	-122.415835599999994
31	4	2	804	2019-09-07 16:00:52.712263	37.7493440000000007	-122.415835599999994
32	4	1	67	2019-09-07 16:11:16.884077	37.7493441000000018	-122.415720100000016
33	4	2	804	2019-09-07 16:11:16.884077	37.7493441000000018	-122.415720100000016
34	4	1	67	2019-09-07 16:13:08.575241	37.7493441000000018	-122.415720100000016
35	4	2	804	2019-09-07 16:13:08.575241	37.7493441000000018	-122.415720100000016
36	4	1	64	2019-09-08 09:52:25.435755	37.7525600999999966	-122.41422249999998
37	4	2	801	2019-09-08 09:52:25.435755	37.7525600999999966	-122.41422249999998
38	1	1	62	2019-09-09 21:14:16.973356	37.7577642999999981	-122.413652200000001
39	1	2	804	2019-09-09 21:14:16.973356	37.7577642999999981	-122.413652200000001
40	1	1	62	2019-09-10 21:40:55.70141	37.749353499999998	-122.415789799999985
41	1	2	801	2019-09-10 21:40:55.70141	37.749353499999998	-122.415789799999985
42	1	1	77	2019-09-11 13:15:05.000358	37.7887051000000014	-122.411524399999976
43	1	2	800	2019-09-11 13:15:05.000358	37.7887051000000014	-122.411524399999976
45	1	1	78	2019-09-11 13:30:48.621404	37.7886887999999956	-122.4115106
46	1	2	800	2019-09-11 13:30:48.621404	37.7886887999999956	-122.4115106
47	1	3	10	2019-09-11 13:30:48.621369	37.7886887999999956	-122.4115106
48	1	2	9	2019-09-11 13:33:31.771339	\N	\N
49	1	1	78	2019-09-11 13:34:34.951697	37.7886914999999988	-122.4115058
50	1	2	800	2019-09-11 13:34:34.951697	37.7886914999999988	-122.4115058
52	1	1	85	2019-09-13 11:41:19.772619	37.7887387999999973	-122.411508799999979
53	1	2	801	2019-09-13 11:41:19.772619	37.7887387999999973	-122.411508799999979
54	1	1	87	2019-09-13 11:52:59.061099	37.7887673999999976	-122.411515999999978
55	1	2	801	2019-09-13 11:52:59.061099	37.7887673999999976	-122.411515999999978
56	1	1	88	2019-09-13 12:37:32.673002	37.7887348000000003	-122.411517599999996
57	1	2	801	2019-09-13 12:37:32.673002	37.7887348000000003	-122.411517599999996
58	1	1	88	2019-09-13 12:41:22.198505	37.7887661999999978	-122.41170910000001
59	1	2	801	2019-09-13 12:41:22.198505	37.7887661999999978	-122.41170910000001
60	1	1	88	2019-09-13 12:45:28.613897	37.7887298999999999	-122.411523199999976
61	1	2	801	2019-09-13 12:45:28.613897	37.7887298999999999	-122.411523199999976
62	1	1	89	2019-09-13 12:54:02.475824	37.7887387999999973	-122.411512300000012
63	1	2	801	2019-09-13 12:54:02.475824	37.7887387999999973	-122.411512300000012
64	1	1	91	2019-09-13 15:35:42.49733	37.7887197999999955	-122.411559700000012
65	1	2	802	2019-09-13 15:35:42.49733	37.7887197999999955	-122.411559700000012
66	1	1	92	2019-09-13 16:18:08.039989	37.7886716000000007	-122.411516999999989
67	1	2	802	2019-09-13 16:18:08.039989	37.7886716000000007	-122.411516999999989
68	1	1	92	2019-09-13 16:23:05.10189	37.7886791999999971	-122.41152910000001
69	1	2	802	2019-09-13 16:23:05.10189	37.7886791999999971	-122.41152910000001
70	1	1	69	2019-09-16 15:54:58.122126	37.7887349999999955	-122.411528599999997
71	1	2	800	2019-09-16 15:54:58.122126	37.7887349999999955	-122.411528599999997
72	1	1	69	2019-09-16 16:00:11.057635	37.7887142999999952	-122.411531299999979
73	1	2	800	2019-09-16 16:00:11.057635	37.7887142999999952	-122.411531299999979
74	1	4	10	2019-09-03 15:00:00	\N	\N
75	1	1	70	2019-09-17 15:46:36.877217	37.7886985999999965	-122.411520199999998
76	1	2	800	2019-09-17 15:46:36.877217	37.7886985999999965	-122.411520199999998
77	1	1	69	2019-09-17 16:16:32.817939	37.7887215000000083	-122.411530000000013
78	1	2	801	2019-09-17 16:16:32.817939	37.7887215000000083	-122.411530000000013
79	1	1	62	2019-09-17 21:18:30.348241	37.7493452000000005	-122.415798299999992
80	1	2	801	2019-09-17 21:18:30.348241	37.7493452000000005	-122.415798299999992
\.


--
-- Data for Name: influences; Type: TABLE DATA; Schema: public; Owner: courtneyholcomb
--

COPY public.influences (id, user_id, label, scale) FROM stdin;
1	1	temperature	125
2	1	weather	1000
3	1	busy	10
4	1	stress	10
5	4	stress	10
6	1	mercury retrograde	10
7	1	rain	10
8	1	sun	10
\.


--
-- Data for Name: symptom_events; Type: TABLE DATA; Schema: public; Owner: courtneyholcomb
--

COPY public.symptom_events (id, user_id, symptom_id, intensity, "timestamp", latitude, longitude) FROM stdin;
1	1	1	10	2019-08-23 13:11:24.556072	\N	\N
6	1	9	10	2019-09-03 20:00:00	\N	\N
7	1	9	10	2019-09-03 21:00:00	\N	\N
8	1	9	5	2019-09-03 22:00:00	\N	\N
9	1	7	10	2019-09-03 22:00:00	\N	\N
10	1	12	10	2019-09-03 17:00:00	\N	\N
11	1	8	10	2019-09-03 12:00:00	\N	\N
\.


--
-- Data for Name: symptoms; Type: TABLE DATA; Schema: public; Owner: courtneyholcomb
--

COPY public.symptoms (id, user_id, label, scale) FROM stdin;
1	1	happiness	10
2	1	headache	10
3	1	acne	10
5	4	headache	100
6	1	lethargy	100
7	1	poor sleep	10
8	1	irritability	10
9	1	anxiety	10
12	1	pain	10
13	1	fullness	10
16	1	high energy	10
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: courtneyholcomb
--

COPY public.users (id, email, username, password, gcal_token) FROM stdin;
1	me@me.com	me	$2b$12$eJOkwW6KWIwiumFRF38ju.ibAHtudGB1Ypij7dRcDb5Ql4BjRnPwu	\\x80049539020000000000008c19676f6f676c652e6f61757468322e63726564656e7469616c73948c0b43726564656e7469616c739493942981947d94288c05746f6b656e948c81796132392e476c75484235496c4250745135467154394c774d69744b3976757a4b626c6a36726e444151373355383368437834617a3162584d4750437471344b436c426a5238334253304a6c6d65717a314147483879474e6336365666534b5673557934416e42334d47554b5f5f61526b7a4a774e5f467a7439374d4a78697639948c06657870697279948c086461746574696d65948c086461746574696d65949394430a07e3091205130206e16794859452948c075f73636f706573945d948c3168747470733a2f2f7777772e676f6f676c65617069732e636f6d2f617574682f63616c656e6461722e726561646f6e6c7994618c0e5f726566726573685f746f6b656e948c2d312f57706c74493439544e4f78426c576975796b6a7062624832714831547934467359675f4c4d7a6851454759948c095f69645f746f6b656e944e8c0a5f746f6b656e5f757269948c2368747470733a2f2f6f61757468322e676f6f676c65617069732e636f6d2f746f6b656e948c0a5f636c69656e745f6964948c483832393233353139363634312d6238707064757566363575756731313365366a676a76386b356e356d6a66716a2e617070732e676f6f676c6575736572636f6e74656e742e636f6d948c0e5f636c69656e745f736563726574948c185355426b51666437784a6d344430385536747a5336335f709475622e
2	hi@hi.com	hi	$2b$12$NyDaDkC7PJ7QEq2GcHl85OYrBxgV8N4TXV/sMWu0frl930b3SqX4u	\\x80049539020000000000008c19676f6f676c652e6f61757468322e63726564656e7469616c73948c0b43726564656e7469616c739493942981947d94288c05746f6b656e948c81796132392e476c743042786c756d703856505f505655732d3345434461624364425a73727970616d2d6e5164693748436e3659426f764b584d49715a48576a78736e7148734c78444363546a436a53725442325f6764736a36362d436e77554d556b6730484e70446a635052715f43424c54575f7762795a5167424a7936654274948c06657870697279948c086461746574696d65948c086461746574696d65949394430a07e3081e15140c0ee3c894859452948c075f73636f706573945d948c3168747470733a2f2f7777772e676f6f676c65617069732e636f6d2f617574682f63616c656e6461722e726561646f6e6c7994618c0e5f726566726573685f746f6b656e948c2d312f6578585a647559305869336f424f374f6571303637797761697a57694b664e7a44776632675a6333506e49948c095f69645f746f6b656e944e8c0a5f746f6b656e5f757269948c2368747470733a2f2f6f61757468322e676f6f676c65617069732e636f6d2f746f6b656e948c0a5f636c69656e745f6964948c483832393233353139363634312d6238707064757566363575756731313365366a676a76386b356e356d6a66716a2e617070732e676f6f676c6575736572636f6e74656e742e636f6d948c0e5f636c69656e745f736563726574948c185355426b51666437784a6d344430385536747a5336335f709475622e
3	hiho@hi.com	hiho	$2b$12$GPCe4RpRy37/bBXX.tbSV.LcuDu0E4S2atoWWn2W9doTE9BZD7tAW	\N
4	metoo@hi.com	metoo	$2b$12$XkFxVU46DGsyYvUUKpQC4egbLqTPVJpIixt5eypmBb5624qm2UR/W	\\x8004953f020000000000008c19676f6f676c652e6f61757468322e63726564656e7469616c73948c0b43726564656e7469616c739493942981947d94288c05746f6b656e948c87796132392e496c3939427a78662d65785f7a784f4f7a4363736f5551565f5f5531545674764234314455574c7369435a63524361382d52434e484c6e44386c4b697931704646497174485f32395f4734446945555a454335646b48696b336b6c544538316747515a5677326e6f686f6844773441586d636c74472d327376793534577073675151948c06657870697279948c086461746574696d65948c086461746574696d65949394430a07e309080023160b293494859452948c075f73636f706573945d948c3168747470733a2f2f7777772e676f6f676c65617069732e636f6d2f617574682f63616c656e6461722e726561646f6e6c7994618c0e5f726566726573685f746f6b656e948c2d312f7077515752786267553537366f42367a626247444c363644644464672d4878535178527973397543705651948c095f69645f746f6b656e944e8c0a5f746f6b656e5f757269948c2368747470733a2f2f6f61757468322e676f6f676c65617069732e636f6d2f746f6b656e948c0a5f636c69656e745f6964948c483832393233353139363634312d6238707064757566363575756731313365366a676a76386b356e356d6a66716a2e617070732e676f6f676c6575736572636f6e74656e742e636f6d948c0e5f636c69656e745f736563726574948c185355426b51666437784a6d344430385536747a5336335f709475622e
5	new@new.com	new	$2b$12$KbvCDzPqSmkZYbTXzncs8.vhOgZjCA47vV08LcKRtOky6hRQN5uIu	\N
6	goo@goo.com	goo	$2b$12$NxXMXZob6fWroD8RcwI0MOuUM.f5Tl0iRM7bLthBkgUrbMpPbeXEG	\\x8004953f020000000000008c19676f6f676c652e6f61757468322e63726564656e7469616c73948c0b43726564656e7469616c739493942981947d94288c05746f6b656e948c87796132392e496c2d4342325153696c48654656644a4e306947327372694e4d395541426b6b516f31304c6b74594831475f715530444f314b4b36495a415f304f79716d487a7a7a41593750696b74794739427a49524d6f4168592d444f695a6e7a5554424a756975694c76626d47787158396a4962366d58507969316b447a4b434a4e2d515777948c06657870697279948c086461746574696d65948c086461746574696d65949394430a07e3090d14140d06f7ab94859452948c075f73636f706573945d948c3168747470733a2f2f7777772e676f6f676c65617069732e636f6d2f617574682f63616c656e6461722e726561646f6e6c7994618c0e5f726566726573685f746f6b656e948c2d312f5a446f7a3868716351796d4a5953596d43706b776f51527a637043544253466f696a2d324f73444e624838948c095f69645f746f6b656e944e8c0a5f746f6b656e5f757269948c2368747470733a2f2f6f61757468322e676f6f676c65617069732e636f6d2f746f6b656e948c0a5f636c69656e745f6964948c483832393233353139363634312d6238707064757566363575756731313365366a676a76386b356e356d6a66716a2e617070732e676f6f676c6575736572636f6e74656e742e636f6d948c0e5f636c69656e745f736563726574948c185355426b51666437784a6d344430385536747a5336335f709475622e
\.


--
-- Name: goals_id_seq; Type: SEQUENCE SET; Schema: public; Owner: courtneyholcomb
--

SELECT pg_catalog.setval('public.goals_id_seq', 1, false);


--
-- Name: habit_events_id_seq; Type: SEQUENCE SET; Schema: public; Owner: courtneyholcomb
--

SELECT pg_catalog.setval('public.habit_events_id_seq', 106, true);


--
-- Name: habits_id_seq; Type: SEQUENCE SET; Schema: public; Owner: courtneyholcomb
--

SELECT pg_catalog.setval('public.habits_id_seq', 26, true);


--
-- Name: influence_events_id_seq; Type: SEQUENCE SET; Schema: public; Owner: courtneyholcomb
--

SELECT pg_catalog.setval('public.influence_events_id_seq', 80, true);


--
-- Name: influences_id_seq; Type: SEQUENCE SET; Schema: public; Owner: courtneyholcomb
--

SELECT pg_catalog.setval('public.influences_id_seq', 8, true);


--
-- Name: symptom_events_id_seq; Type: SEQUENCE SET; Schema: public; Owner: courtneyholcomb
--

SELECT pg_catalog.setval('public.symptom_events_id_seq', 11, true);


--
-- Name: symptoms_id_seq; Type: SEQUENCE SET; Schema: public; Owner: courtneyholcomb
--

SELECT pg_catalog.setval('public.symptoms_id_seq', 16, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: courtneyholcomb
--

SELECT pg_catalog.setval('public.users_id_seq', 6, true);


--
-- Name: goals goals_pkey; Type: CONSTRAINT; Schema: public; Owner: courtneyholcomb
--

ALTER TABLE ONLY public.goals
    ADD CONSTRAINT goals_pkey PRIMARY KEY (id);


--
-- Name: habit_events habit_events_pkey; Type: CONSTRAINT; Schema: public; Owner: courtneyholcomb
--

ALTER TABLE ONLY public.habit_events
    ADD CONSTRAINT habit_events_pkey PRIMARY KEY (id);


--
-- Name: habits habits_pkey; Type: CONSTRAINT; Schema: public; Owner: courtneyholcomb
--

ALTER TABLE ONLY public.habits
    ADD CONSTRAINT habits_pkey PRIMARY KEY (id);


--
-- Name: influence_events influence_events_pkey; Type: CONSTRAINT; Schema: public; Owner: courtneyholcomb
--

ALTER TABLE ONLY public.influence_events
    ADD CONSTRAINT influence_events_pkey PRIMARY KEY (id);


--
-- Name: influences influences_pkey; Type: CONSTRAINT; Schema: public; Owner: courtneyholcomb
--

ALTER TABLE ONLY public.influences
    ADD CONSTRAINT influences_pkey PRIMARY KEY (id);


--
-- Name: symptom_events symptom_events_pkey; Type: CONSTRAINT; Schema: public; Owner: courtneyholcomb
--

ALTER TABLE ONLY public.symptom_events
    ADD CONSTRAINT symptom_events_pkey PRIMARY KEY (id);


--
-- Name: symptoms symptoms_pkey; Type: CONSTRAINT; Schema: public; Owner: courtneyholcomb
--

ALTER TABLE ONLY public.symptoms
    ADD CONSTRAINT symptoms_pkey PRIMARY KEY (id);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: courtneyholcomb
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: courtneyholcomb
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: users users_username_key; Type: CONSTRAINT; Schema: public; Owner: courtneyholcomb
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- Name: goals goals_habit_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: courtneyholcomb
--

ALTER TABLE ONLY public.goals
    ADD CONSTRAINT goals_habit_id_fkey FOREIGN KEY (habit_id) REFERENCES public.habits(id);


--
-- Name: goals goals_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: courtneyholcomb
--

ALTER TABLE ONLY public.goals
    ADD CONSTRAINT goals_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: habit_events habit_events_habit_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: courtneyholcomb
--

ALTER TABLE ONLY public.habit_events
    ADD CONSTRAINT habit_events_habit_id_fkey FOREIGN KEY (habit_id) REFERENCES public.habits(id);


--
-- Name: habit_events habit_events_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: courtneyholcomb
--

ALTER TABLE ONLY public.habit_events
    ADD CONSTRAINT habit_events_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: habits habits_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: courtneyholcomb
--

ALTER TABLE ONLY public.habits
    ADD CONSTRAINT habits_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: influence_events influence_events_influence_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: courtneyholcomb
--

ALTER TABLE ONLY public.influence_events
    ADD CONSTRAINT influence_events_influence_id_fkey FOREIGN KEY (influence_id) REFERENCES public.influences(id);


--
-- Name: influence_events influence_events_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: courtneyholcomb
--

ALTER TABLE ONLY public.influence_events
    ADD CONSTRAINT influence_events_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: influences influences_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: courtneyholcomb
--

ALTER TABLE ONLY public.influences
    ADD CONSTRAINT influences_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: symptom_events symptom_events_symptom_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: courtneyholcomb
--

ALTER TABLE ONLY public.symptom_events
    ADD CONSTRAINT symptom_events_symptom_id_fkey FOREIGN KEY (symptom_id) REFERENCES public.symptoms(id);


--
-- Name: symptom_events symptom_events_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: courtneyholcomb
--

ALTER TABLE ONLY public.symptom_events
    ADD CONSTRAINT symptom_events_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: symptoms symptoms_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: courtneyholcomb
--

ALTER TABLE ONLY public.symptoms
    ADD CONSTRAINT symptoms_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- PostgreSQL database dump complete
--

