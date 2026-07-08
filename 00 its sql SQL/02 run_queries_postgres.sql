-- run_queries_postgres.sql
-- Seed the database with test data for "School of Developers" (PostgreSQL).
-- Run AFTER 01 schema_postgres.sql, e.g.:
--   psql -U postgres -d timetable_db -f "02 run_queries_postgres.sql"
--
-- Login afterwards with  username: test   password: test

DO $$
DECLARE
  v_school_id INT;
  v_course_id INT;
  v_class_fe  INT;
  v_class_be  INT;
  v_class_do  INT;
  v_class_ai  INT;
  t1 INT; t2 INT; t3 INT; t4 INT; t5 INT; t6 INT; t7 INT; t8 INT;
  t9 INT; t10 INT; t11 INT; t12 INT; t13 INT; t14 INT; t15 INT; t16 INT;
  t17 INT; t18 INT; t19 INT; t20 INT; t21 INT; t22 INT; t23 INT; t24 INT;
  t25 INT; t26 INT; t27 INT; t28 INT; t29 INT; t30 INT; t31 INT; t32 INT;
BEGIN
  -- 1. Create a new school: "School of Developers"
  -- Password 'test' hashed using Werkzeug (scrypt)
  INSERT INTO schools (school_name, username, password_hash, start_time, end_time, lecture_duration, break_start_time, break_duration)
  VALUES ('School of Developers', 'test',
          'scrypt:32768:8:1$9pKNRyRMOG8d2fkM$aed0bcef59a339791d55026d6ae8afdefa38e2c69074510a5273ff2480085352b26aecd0ffe4db300bb75098c164063382a01313234644d0dbb1d871def33c93',
          '09:00', '17:00', 60, '12:00', 60)
  RETURNING school_id INTO v_school_id;

  -- 2. Create a default course
  INSERT INTO course (course_name, school_id) VALUES ('Computer Science', v_school_id) RETURNING course_id INTO v_course_id;

  -- 3. Create 4 Classes
  INSERT INTO class (class_name, school_id) VALUES ('FRONTEND FY', v_school_id) RETURNING class_id INTO v_class_fe;
  INSERT INTO class (class_name, school_id) VALUES ('BACKEND SY', v_school_id) RETURNING class_id INTO v_class_be;
  INSERT INTO class (class_name, school_id) VALUES ('DEVOPS TY', v_school_id) RETURNING class_id INTO v_class_do;
  INSERT INTO class (class_name, school_id) VALUES ('AI & ML BTech', v_school_id) RETURNING class_id INTO v_class_ai;

  -- 4. Teachers and Subjects for FRONTEND FY
  INSERT INTO teacher (teacher_name, school_id) VALUES ('Ada Lovelace', v_school_id) RETURNING teacher_id INTO t1;
  INSERT INTO teacher (teacher_name, school_id) VALUES ('Brendan Eich', v_school_id) RETURNING teacher_id INTO t2;
  INSERT INTO teacher (teacher_name, school_id) VALUES ('Håkon Wium Lie', v_school_id) RETURNING teacher_id INTO t3;
  INSERT INTO teacher (teacher_name, school_id) VALUES ('John Resig', v_school_id) RETURNING teacher_id INTO t4;
  INSERT INTO teacher (teacher_name, school_id) VALUES ('Jordan Walke', v_school_id) RETURNING teacher_id INTO t5;
  INSERT INTO teacher (teacher_name, school_id) VALUES ('Evan You', v_school_id) RETURNING teacher_id INTO t6;
  INSERT INTO teacher (teacher_name, school_id) VALUES ('Dan Abramov', v_school_id) RETURNING teacher_id INTO t7;
  INSERT INTO teacher (teacher_name, school_id) VALUES ('Lea Verou', v_school_id) RETURNING teacher_id INTO t8;

  INSERT INTO subject (subject_name, class_id, course_id, teacher_id, semester, credits, school_id) VALUES
  ('HTML5 Basics', v_class_fe, v_course_id, t1, 1, 4, v_school_id),
  ('JavaScript ES6', v_class_fe, v_course_id, t2, 1, 4, v_school_id),
  ('Modern CSS', v_class_fe, v_course_id, t3, 1, 4, v_school_id),
  ('jQuery Legacy', v_class_fe, v_course_id, t4, 1, 3, v_school_id),
  ('React Fundamentals', v_class_fe, v_course_id, t5, 1, 5, v_school_id),
  ('VueJS Core', v_class_fe, v_course_id, t6, 1, 4, v_school_id),
  ('Redux State', v_class_fe, v_course_id, t7, 1, 3, v_school_id),
  ('Web Accessibility', v_class_fe, v_course_id, t8, 1, 3, v_school_id);

  -- 5. Teachers and Subjects for BACKEND SY
  INSERT INTO teacher (teacher_name, school_id) VALUES ('James Gosling', v_school_id) RETURNING teacher_id INTO t9;
  INSERT INTO teacher (teacher_name, school_id) VALUES ('Guido van Rossum', v_school_id) RETURNING teacher_id INTO t10;
  INSERT INTO teacher (teacher_name, school_id) VALUES ('Dennis Ritchie', v_school_id) RETURNING teacher_id INTO t11;
  INSERT INTO teacher (teacher_name, school_id) VALUES ('Bjarne Stroustrup', v_school_id) RETURNING teacher_id INTO t12;
  INSERT INTO teacher (teacher_name, school_id) VALUES ('Ryan Dahl', v_school_id) RETURNING teacher_id INTO t13;
  INSERT INTO teacher (teacher_name, school_id) VALUES ('Martin Fowler', v_school_id) RETURNING teacher_id INTO t14;
  INSERT INTO teacher (teacher_name, school_id) VALUES ('Robert Martin', v_school_id) RETURNING teacher_id INTO t15;
  INSERT INTO teacher (teacher_name, school_id) VALUES ('Joshua Bloch', v_school_id) RETURNING teacher_id INTO t16;

  INSERT INTO subject (subject_name, class_id, course_id, teacher_id, semester, credits, school_id) VALUES
  ('Java Core', v_class_be, v_course_id, t9, 3, 5, v_school_id),
  ('Python Advanced', v_class_be, v_course_id, t10, 3, 5, v_school_id),
  ('C Programming', v_class_be, v_course_id, t11, 3, 4, v_school_id),
  ('C++ Systems', v_class_be, v_course_id, t12, 3, 4, v_school_id),
  ('NodeJS Runtime', v_class_be, v_course_id, t13, 3, 4, v_school_id),
  ('Microservices', v_class_be, v_course_id, t14, 3, 3, v_school_id),
  ('Clean Code', v_class_be, v_course_id, t15, 3, 3, v_school_id),
  ('API Design', v_class_be, v_course_id, t16, 3, 3, v_school_id);

  -- 6. Teachers and Subjects for DEVOPS TY
  INSERT INTO teacher (teacher_name, school_id) VALUES ('Linus Torvalds', v_school_id) RETURNING teacher_id INTO t17;
  INSERT INTO teacher (teacher_name, school_id) VALUES ('Solomon Hykes', v_school_id) RETURNING teacher_id INTO t18;
  INSERT INTO teacher (teacher_name, school_id) VALUES ('Brendan Burns', v_school_id) RETURNING teacher_id INTO t19;
  INSERT INTO teacher (teacher_name, school_id) VALUES ('Mitchell Hashimoto', v_school_id) RETURNING teacher_id INTO t20;
  INSERT INTO teacher (teacher_name, school_id) VALUES ('Gene Kim', v_school_id) RETURNING teacher_id INTO t21;
  INSERT INTO teacher (teacher_name, school_id) VALUES ('Werner Vogels', v_school_id) RETURNING teacher_id INTO t22;
  INSERT INTO teacher (teacher_name, school_id) VALUES ('Kelsey Hightower', v_school_id) RETURNING teacher_id INTO t23;
  INSERT INTO teacher (teacher_name, school_id) VALUES ('Nicole Forsgren', v_school_id) RETURNING teacher_id INTO t24;

  INSERT INTO subject (subject_name, class_id, course_id, teacher_id, semester, credits, school_id) VALUES
  ('Linux Kernel', v_class_do, v_course_id, t17, 5, 5, v_school_id),
  ('Docker Containers', v_class_do, v_course_id, t18, 5, 4, v_school_id),
  ('Kubernetes Ops', v_class_do, v_course_id, t19, 5, 5, v_school_id),
  ('Terraform IaC', v_class_do, v_course_id, t20, 5, 4, v_school_id),
  ('DevOps Culture', v_class_do, v_course_id, t21, 5, 3, v_school_id),
  ('AWS Cloud', v_class_do, v_course_id, t22, 5, 4, v_school_id),
  ('Serverless', v_class_do, v_course_id, t23, 5, 4, v_school_id),
  ('DORA Metrics', v_class_do, v_course_id, t24, 5, 3, v_school_id);

  -- 7. Teachers and Subjects for AI & ML BTech
  INSERT INTO teacher (teacher_name, school_id) VALUES ('Andrew Ng', v_school_id) RETURNING teacher_id INTO t25;
  INSERT INTO teacher (teacher_name, school_id) VALUES ('Geoffrey Hinton', v_school_id) RETURNING teacher_id INTO t26;
  INSERT INTO teacher (teacher_name, school_id) VALUES ('Yann LeCun', v_school_id) RETURNING teacher_id INTO t27;
  INSERT INTO teacher (teacher_name, school_id) VALUES ('Yoshua Bengio', v_school_id) RETURNING teacher_id INTO t28;
  INSERT INTO teacher (teacher_name, school_id) VALUES ('Fei-Fei Li', v_school_id) RETURNING teacher_id INTO t29;
  INSERT INTO teacher (teacher_name, school_id) VALUES ('Demis Hassabis', v_school_id) RETURNING teacher_id INTO t30;
  INSERT INTO teacher (teacher_name, school_id) VALUES ('Andrej Karpathy', v_school_id) RETURNING teacher_id INTO t31;
  INSERT INTO teacher (teacher_name, school_id) VALUES ('Sam Altman', v_school_id) RETURNING teacher_id INTO t32;

  INSERT INTO subject (subject_name, class_id, course_id, teacher_id, semester, credits, school_id) VALUES
  ('Machine Learning', v_class_ai, v_course_id, t25, 7, 5, v_school_id),
  ('Deep Learning', v_class_ai, v_course_id, t26, 7, 5, v_school_id),
  ('Computer Vision', v_class_ai, v_course_id, t27, 7, 4, v_school_id),
  ('NLP Core', v_class_ai, v_course_id, t28, 7, 4, v_school_id),
  ('Image Processing', v_class_ai, v_course_id, t29, 7, 4, v_school_id),
  ('Reinforcement', v_class_ai, v_course_id, t30, 7, 4, v_school_id),
  ('Tesla Autopilot', v_class_ai, v_course_id, t31, 7, 3, v_school_id),
  ('Generative AI', v_class_ai, v_course_id, t32, 7, 5, v_school_id);
END $$;
