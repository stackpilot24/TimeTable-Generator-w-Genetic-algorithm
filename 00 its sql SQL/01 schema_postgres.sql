-- PostgreSQL schema for the Timetable Generator.
-- Create the database first, then load this file, e.g.:
--   createdb -U postgres timetable_db
--   psql -U postgres -d timetable_db -f "01 schema_postgres.sql"

DROP TABLE IF EXISTS allocated_timeslots CASCADE;
DROP TABLE IF EXISTS practical CASCADE;
DROP TABLE IF EXISTS timetable CASCADE;
DROP TABLE IF EXISTS subject CASCADE;
DROP TABLE IF EXISTS teacher CASCADE;
DROP TABLE IF EXISTS timeslot CASCADE;
DROP TABLE IF EXISTS class CASCADE;
DROP TABLE IF EXISTS course CASCADE;
DROP TABLE IF EXISTS schools CASCADE;

-- Table: schools
CREATE TABLE schools (
  school_id        SERIAL PRIMARY KEY,
  school_name      VARCHAR(100) NOT NULL,
  username         VARCHAR(50)  NOT NULL UNIQUE,
  password_hash    VARCHAR(255) NOT NULL,
  -- 'school' hides semester/credits in the UI; 'college'/'university' show them.
  school_type      VARCHAR(20)  NOT NULL DEFAULT 'school',
  start_time       VARCHAR(10),
  end_time         VARCHAR(10),
  lecture_duration INT,
  break_start_time VARCHAR(10),
  break_duration   INT
);

-- Table: course (Linked to School)
CREATE TABLE course (
  course_id   SERIAL PRIMARY KEY,
  course_name VARCHAR(20) NOT NULL,
  school_id   INT NOT NULL REFERENCES schools (school_id) ON DELETE CASCADE
);

-- Table: class (Linked to School)
CREATE TABLE class (
  class_id   SERIAL PRIMARY KEY,
  class_name VARCHAR(20) NOT NULL,
  school_id  INT NOT NULL REFERENCES schools (school_id) ON DELETE CASCADE
);

-- Table: room (Linked to School)
CREATE TABLE room (
  room_id   SERIAL PRIMARY KEY,
  room_name VARCHAR(20) NOT NULL,
  room_type VARCHAR(20) NOT NULL CHECK (room_type IN ('practical', 'lecture')),
  school_id INT NOT NULL REFERENCES schools (school_id) ON DELETE CASCADE
);

-- Table: teacher (Linked to School)
CREATE TABLE teacher (
  teacher_id   SERIAL PRIMARY KEY,
  teacher_name VARCHAR(100) NOT NULL,
  school_id    INT NOT NULL REFERENCES schools (school_id) ON DELETE CASCADE
);

-- Table: timeslot
CREATE TABLE timeslot (
  time_id       SERIAL PRIMARY KEY,
  timeslot      TIME NOT NULL,
  type_of_class VARCHAR(20) NOT NULL CHECK (type_of_class IN ('lecture', 'practical'))
);

-- Table: subject (Linked to School)
CREATE TABLE subject (
  subject_id   SERIAL PRIMARY KEY,
  subject_name VARCHAR(20) NOT NULL,
  class_id     INT NOT NULL REFERENCES class (class_id),
  course_id    INT NOT NULL REFERENCES course (course_id),
  teacher_id   INT NOT NULL REFERENCES teacher (teacher_id),
  semester     INT NOT NULL,
  credits      INT DEFAULT 4,
  school_id    INT NOT NULL REFERENCES schools (school_id) ON DELETE CASCADE
);

-- Table: timetable (Linked to School)
CREATE TABLE timetable (
  timetable_id SERIAL PRIMARY KEY,
  teacher_id   INT NOT NULL,
  subject_id   INT NOT NULL,
  class_id     INT NOT NULL,
  course_id    INT NOT NULL,
  time_id      INT NOT NULL,
  day          VARCHAR(15) DEFAULT NULL,
  school_id    INT NOT NULL REFERENCES schools (school_id) ON DELETE CASCADE
);

-- Table: allocated_timeslots
CREATE TABLE allocated_timeslots (
  allocation_id SERIAL PRIMARY KEY,
  teacher_id    INT NOT NULL REFERENCES teacher (teacher_id),
  subject_id    INT NOT NULL REFERENCES subject (subject_id),
  time_id       INT NOT NULL REFERENCES timeslot (time_id),
  school_id     INT NOT NULL REFERENCES schools (school_id) ON DELETE CASCADE
);

-- Table: practical
CREATE TABLE practical (
  practical_id   SERIAL PRIMARY KEY,
  practical_name VARCHAR(20) NOT NULL,
  time_id        INT NOT NULL REFERENCES timeslot (time_id),
  room_id        INT NOT NULL REFERENCES room (room_id),
  class_id       INT NOT NULL REFERENCES class (class_id),
  school_id      INT NOT NULL REFERENCES schools (school_id) ON DELETE CASCADE
);
