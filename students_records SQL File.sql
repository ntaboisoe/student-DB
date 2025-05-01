--------------------------------------------------------------------
/*
 * STUDENT RECORDS DATABSE
 * @Table 1 => Students Details
 * @Table 2 => Courses Details
 * @Table 3 => Teachers Details
 * @Table 4 => Teachers to Courses
 * @Table 5 => Students to Courses
 * @Table 6 => Course Attendance
 * 
 * */
--------------------------------------------------------------------
/*DROP TABLES TO ALLOW FOR TESTING*/
DROP TABLE IF EXISTS attendance;
DROP TABLE IF EXISTS students_courses;
DROP TABLE IF EXISTS course_teacher;
DROP TABLE IF EXISTS teachers;
DROP TABLE IF EXISTS courses;
DROP TABLE IF EXISTS students;
--------------------------------------------------------------------

CREATE TABLE students(
	student_id int PRIMARY KEY,
	student_name varchar(200) NOT NULL,
	student_age int NOT NULL,
	student_email varchar(200) NOT NULL UNIQUE
);
CREATE TABLE courses(
	course_id int PRIMARY KEY,
	course_name varchar(200) NOT NULL
);
CREATE TABLE teachers(
	teacher_id int PRIMARY KEY,
	teacher_name varchar(200) NOT NULL,
	teacher_email varchar(200) NOT NULL UNIQUE
);
CREATE TABLE course_teacher(
	teacher_id int,
	course_id int,
	PRIMARY KEY (teacher_id, course_id),
	FOREIGN KEY (teacher_id) REFERENCES teachers (teacher_id) ON DELETE CASCADE,
	FOREIGN KEY (course_id) REFERENCES courses (course_id) ON DELETE CASCADE
);
CREATE TABLE students_courses(
	student_id int,
	course_id int,
	PRIMARY KEY (student_id,course_id),
	FOREIGN KEY (student_id) REFERENCES students (student_id) ON DELETE CASCADE,
	FOREIGN KEY (course_id) REFERENCES courses (course_id) ON DELETE CASCADE
);
CREATE TABLE attendance(
	course_id int NOT NULL,
	student_id int NOT NULL,
	class_date date NOT NULL,
	class_start_time time NOT NULL,
	class_end_time time NOT NULL,
	attendance_status varchar(200) NOT NULL,
	PRIMARY KEY (course_id, student_id, class_date, class_start_time),
	FOREIGN KEY (course_id) REFERENCES courses (course_id) ON DELETE CASCADE,
	FOREIGN KEY (student_id) REFERENCES students (student_id) ON DELETE CASCADE
);

--------------------------------------------------------------------
/*INSERTING DATA INTO THE TABLES*/

-- Insert Courses
INSERT INTO courses (course_id, course_name)
VALUES
	(1, 'Python'),
	(2, 'Database Design & Programming with SQL'),
	(3, 'Startup Building for Developers'),
	(4, 'Software Development'),
	(5, 'Web Development');

-- Insert Teachers
INSERT INTO teachers (teacher_id, teacher_name, teacher_email)
VALUES
	(1, 'Evans Mutuku', 'evans@example.org'),
	(2, 'Gerald Macherechedze', 'gerald@example.org'),
	(3, 'Nelly Alili', 'plpsoftskills@gmail.com'),
	(4, 'Zablon Oigo', 'zablon@example.org');

-- Insert Students
INSERT INTO students (student_id, student_name, student_age, student_email)
VALUES
	(1, 'Hassan Nur', 31, 'hassan.nur@example.com'),
	(2, 'Faith Osadiaye', 28, 'faith.osadiaye@example.com'),
	(3, 'Timothy Monejo', 26, 'timothy.monejo@example.com'),
	(4, 'Sekinat Oladejo', 33, 'sekinat.oladejo@example.com'),
	(5, 'Shalom Mbuthia', 29, 'shalom.mbuthia@example.com'),
	(6, 'Mbali Gamede', 27, 'mbali.gamede@example.com'),
	(7, 'Abdulbasit Shukri', 30, 'abdulbasit.shukri@example.com'),
	(8, 'Robert Isoe', 35, 'robert.isoe@example.com'),
	(9, 'Mugisha Leonce', 32, 'mugisha.leonce@example.com'),
	(10, 'Rehema Maina', 25, 'rehema.maina@example.com'),
	(11, 'Samuel Githaiga', 34, 'samuel.githaiga@example.com');

-- Assign Teachers to Courses (course_teacher table)
INSERT INTO course_teacher (teacher_id, course_id)
	VALUES
	(1, 1), -- Evans Mutuku teaches Python
	(1, 4), -- Evans Mutuku teaches Software Development
	(2, 2), -- Gerald Macherechedze teaches Database Design
	(2, 3), -- Gerald Macherechedze teaches Startup Building
	(3, 3), -- Nelly Alili teaches Startup Building
	(4, 4), -- Zablon Oigo teaches Software Development
	(4, 5); -- Zablon Oigo teaches Web Development


-- Enroll Students in Courses (students_courses table)
INSERT INTO students_courses (student_id, course_id)
VALUES
	(1, 1), (1, 2), -- Hassan in Python, Database
	(2, 1), (2, 5), -- Faith in Python, Web Dev
	(3, 2), (3, 3), -- Timothy in Database, Startup Building
	(4, 1), (4, 4), (4, 5), -- Sekinat in Python, Software Dev, Web Dev
	(5, 2), (5, 3), (5, 4), -- Shalom in Database, Startup Building, Software Dev
	(6, 1), -- Mbali in Python
	(7, 5), -- Abdulbasit in Web Dev
	(8, 2), -- Robert in Database
	(9, 3), -- Mugisha in Startup Building
	(10, 4), -- Rehema in Software Dev
	(11, 1), (11, 5); -- Samuel in Python, Web Dev


-- Record Attendance (attendance table) Date: 2025-11-05

-- Session 1: Python (Course 1) on 2025-11-05, 09:00 - 10:30
INSERT INTO attendance (course_id, student_id, class_date, class_start_time, class_end_time, attendance_status)
VALUES
	(1, 1, '2025-11-05', '09:00:00', '10:30:00', 'Present'), -- Hassan Present
	(1, 2, '2025-11-05', '09:00:00', '10:30:00', 'Present'), -- Faith Present
	(1, 4, '2025-11-05', '09:00:00', '10:30:00', 'Late'),    -- Sekinat Late
	(1, 6, '2025-11-05', '09:00:00', '10:30:00', 'Absent'),  -- Mbali Absent
	(1, 11, '2025-11-05', '09:00:00', '10:30:00', 'Present');-- Samuel Present

-- Session 2: Database Design (Course 2) on 2025-11-05, 11:00 - 12:30
INSERT INTO attendance (course_id, student_id, class_date, class_start_time, class_end_time, attendance_status)
VALUES
	(2, 1, '2025-11-05', '11:00:00', '12:30:00', 'Present'), -- Hassan Present
	(2, 3, '2025-11-05', '11:00:00', '12:30:00', 'Present'), -- Timothy Present
	(2, 5, '2025-11-05', '11:00:00', '12:30:00', 'Absent'),  -- Shalom Absent
	(2, 8, '2025-11-05', '11:00:00', '12:30:00', 'Present'); -- Robert Present

-- Session 3: Web Development (Course 5) on 2025-11-05, 14:00 - 15:30
INSERT INTO attendance (course_id, student_id, class_date, class_start_time, class_end_time, attendance_status)
VALUES
	(5, 2, '2025-11-05', '14:00:00', '15:30:00', 'Present'),  -- Faith Present
	(5, 4, '2025-11-05', '14:00:00', '15:30:00', 'Present'),  -- Sekinat Present
	(5, 7, '2025-11-05', '14:00:00', '15:30:00', 'Present'),  -- Abdulbasit Present
	(5, 11, '2025-11-05', '14:00:00', '15:30:00', 'Present'); -- Samuel Present