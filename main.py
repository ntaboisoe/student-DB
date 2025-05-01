# Save this code as main.py

from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
import aiosqlite
import os
from datetime import date, time # Import date and time
# Import datetime for time formatting if needed later, but time.isoformat() is often sufficient
# from datetime import datetime

# --- Database Configuration ---
DATABASE_URL = "sqlite:///./student_records.db" # Relative path to the database file

# --- Database Initialization ---
async def init_db():
    """Initializes the database schema and populates with sample data if DB doesn't exist."""
    # Use the schema provided earlier, adjusted for TEXT and attendance_status
    # Added DROP TABLE statements to make it easy to rerun during development
    schema_sql = """
    PRAGMA foreign_keys = ON; -- Ensure foreign key constraints are enforced

    DROP TABLE IF EXISTS attendance;
    DROP TABLE IF EXISTS students_courses;
    DROP TABLE IF EXISTS course_teacher;
    DROP TABLE IF EXISTS teachers;
    DROP TABLE IF EXISTS courses;
    DROP TABLE IF EXISTS students;

    CREATE TABLE students(
        student_id INTEGER PRIMARY KEY, -- Or INTEGER PRIMARY KEY AUTOINCREMENT
        student_name TEXT NOT NULL,
        student_age INTEGER NOT NULL,
        student_email TEXT NOT NULL UNIQUE
    );

    CREATE TABLE courses(
        course_id INTEGER PRIMARY KEY, -- Or INTEGER PRIMARY KEY AUTOINCREMENT
        course_name TEXT NOT NULL
    );

    CREATE TABLE teachers(
        teacher_id INTEGER PRIMARY KEY, -- Or INTEGER PRIMARY KEY AUTOINCREMENT
        teacher_name TEXT NOT NULL,
        teacher_email TEXT NOT NULL UNIQUE
    );

    CREATE TABLE course_teacher(
        teacher_id INTEGER,
        course_id INTEGER,
        PRIMARY KEY (teacher_id, course_id),
        FOREIGN KEY (teacher_id) REFERENCES teachers (teacher_id) ON DELETE CASCADE,
        FOREIGN KEY (course_id) REFERENCES courses (course_id) ON DELETE CASCADE
    );

    CREATE TABLE students_courses(
        student_id INTEGER,
        course_id INTEGER,
        PRIMARY KEY (student_id, course_id),
        FOREIGN KEY (student_id) REFERENCES students (student_id) ON DELETE CASCADE,
        FOREIGN KEY (course_id) REFERENCES courses (course_id) ON DELETE CASCADE
    );

    CREATE TABLE attendance(
        course_id INTEGER NOT NULL,
        student_id INTEGER NOT NULL,
        class_date DATE NOT NULL,
        class_start_time TIME NOT NULL,
        class_end_time TIME NOT NULL, -- Assuming you still want end time
        attendance_status TEXT NOT NULL, -- Added column for status (e.g., 'Present', 'Absent')
        PRIMARY KEY (course_id, student_id, class_date, class_start_time),

        -- Existing FKs (still needed to ensure the student and course exist at all)
        FOREIGN KEY (course_id) REFERENCES courses (course_id) ON DELETE CASCADE,
        FOREIGN KEY (student_id) REFERENCES students (student_id) ON DELETE CASCADE,

        -- NEW FK: Reference the composite PK of students_courses to ensure enrollment
        FOREIGN KEY (student_id, course_id) REFERENCES students_courses (student_id, course_id) ON DELETE CASCADE
    );
    """

    # User's provided INSERT statements
    insert_sql = """
    -- Insert Courses
    INSERT INTO courses (course_id, course_name) VALUES
        (1, 'Python'),
        (2, 'Database Design & Programming with SQL'),
        (3, 'Startup Building for Developers'),
        (4, 'Software Development'),
        (5, 'Web Development');

    -- Insert Teachers
    INSERT INTO teachers (teacher_id, teacher_name, teacher_email) VALUES
        (1, 'Evans Mutuku', 'evans@example.org'),
        (2, 'Gerald Macherechedze', 'gerald@example.org'),
        (3, 'Nelly Alili', 'plpsoftskills@gmail.com'),
        (4, 'Zablon Oigo', 'zablon@example.org');

    -- Insert Students
    INSERT INTO students (student_id, student_name, student_age, student_email) VALUES
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
    INSERT INTO course_teacher (teacher_id, course_id) VALUES
        (1, 1), -- Evans Mutuku teaches Python
        (1, 4), -- Evans Mutuku teaches Software Development
        (2, 2), -- Gerald Macherechedze teaches Database Design
        (2, 3), -- Gerald Macherechedze teaches Startup Building
        (3, 3), -- Nelly Alili teaches Startup Building
        (4, 4), -- Zablon Oigo teaches Software Development
        (4, 5); -- Zablon Oigo teaches Web Development


    -- Enroll Students in Courses (students_courses table)
    INSERT INTO students_courses (student_id, course_id) VALUES
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
    -- Note: These inserts must follow the enrollments above to satisfy the new FK

    -- Session 1: Python (Course 1) on 2025-11-05, 09:00 - 10:30
    INSERT INTO attendance (course_id, student_id, class_date, class_start_time, class_end_time, attendance_status) VALUES
        (1, 1, '2025-11-05', '09:00:00', '10:30:00', 'Present'), -- Hassan Present (Hassan is in course 1)
        (1, 2, '2025-11-05', '09:00:00', '10:30:00', 'Present'), -- Faith Present (Faith is in course 1)
        (1, 4, '2025-11-05', '09:00:00', '10:30:00', 'Late'),    -- Sekinat Late (Sekinat is in course 1)
        (1, 6, '2025-11-05', '09:00:00', '10:30:00', 'Absent'),  -- Mbali Absent (Mbali is in course 1)
        (1, 11, '2025-11-05', '09:00:00', '10:30:00', 'Present');-- Samuel Present (Samuel is in course 1)

    -- Session 2: Database Design (Course 2) on 2025-11-05, 11:00 - 12:30
    INSERT INTO attendance (course_id, student_id, class_date, class_start_time, class_end_time, attendance_status) VALUES
        (2, 1, '2025-11-05', '11:00:00', '12:30:00', 'Present'), -- Hassan Present (Hassan is in course 2)
        (2, 3, '2025-11-05', '11:00:00', '12:30:00', 'Present'), -- Timothy Present (Timothy is in course 2)
        (2, 5, '2025-11-05', '11:00:00', '12:30:00', 'Absent'),  -- Shalom Absent (Shalom is in course 2)
        (2, 8, '2025-11-05', '11:00:00', '12:30:00', 'Present'); -- Robert Present (Robert is in course 2)

    -- Session 3: Web Development (Course 5) on 2025-11-05, 14:00 - 15:30
    INSERT INTO attendance (course_id, student_id, class_date, class_start_time, class_end_time, attendance_status) VALUES
        (5, 2, '2025-11-05', '14:00:00', '15:30:00', 'Present'),  -- Faith Present (Faith is in course 5)
        (5, 4, '2025-11-05', '14:00:00', '15:30:00', 'Present'),  -- Sekinat Present (Sekinat is in course 5)
        (5, 7, '2025-11-05', '14:00:00', '15:30:00', 'Present'),  -- Abdulbasit Shukri Present (Abdulbasit is in course 5)
        (5, 11, '2025-11-05', '14:00:00', '15:30:00', 'Present'); -- Samuel Githaiga Present (Samuel is in course 5)
    """


    db_file = DATABASE_URL.replace("sqlite:///","")
    if not os.path.exists(db_file):
        async with aiosqlite.connect(db_file) as db:
            # Ensure foreign key constraints are on when creating schema
            await db.execute("PRAGMA foreign_keys = ON;")

            print("Database file not found. Creating schema...")
            await db.executescript(schema_sql)
            await db.commit()
            print("Database schema created!")

            # Execute sample data inserts
            print("Inserting sample data...")
            # The sample insert_sql already contains string formats for date/time
            await db.executescript(insert_sql)
            await db.commit()
            print("Sample data inserted!")
    else:
        print("Database file already exists. Schema and sample data not recreated.")


# --- Database Dependency ---
async def get_db():
    """Provides an asynchronous database connection."""
    # ensure check_same_thread=False is used for aiosqlite connections, especially with FastAPI
    # By default, aiosqlite handles this appropriately in async context, but explicit is clearer
    db = await aiosqlite.connect(DATABASE_URL.replace("sqlite:///",""), check_same_thread=False)
    # Ensure foreign key constraints are on for this connection
    await db.execute("PRAGMA foreign_keys = ON;")
    db.row_factory = aiosqlite.Row # Allows accessing columns by name
    try:
        yield db
    finally:
        await db.close()

# --- Pydantic Models ---

class StudentBase(BaseModel):
    student_name: str
    student_age: int
    student_email: str

class StudentCreate(StudentBase):
    # student_id will be provided manually or auto-generated by DB if AUTOINCREMENT is used
    pass # student_id is not required for creation if DB auto-generates

class Student(StudentBase):
    student_id: int

    class Config:
        orm_mode = True # Compatibility with ORM-like behavior (fetching from DB rows)
        from_attributes = True # New name for orm_mode in Pydantic V2

class CourseBase(BaseModel):
    course_name: str

class CourseCreate(CourseBase):
    pass

class Course(CourseBase):
    course_id: int

    class Config:
        orm_mode = True
        from_attributes = True

class TeacherBase(BaseModel):
    teacher_name: str
    teacher_email: str

class TeacherCreate(TeacherBase):
    pass

class Teacher(TeacherBase):
    teacher_id: int

    class Config:
        orm_mode = True
        from_attributes = True

class CourseTeacherBase(BaseModel):
    teacher_id: int
    course_id: int

class CourseTeacherCreate(CourseTeacherBase):
    pass

class CourseTeacher(CourseTeacherBase):
     class Config:
        orm_mode = True
        from_attributes = True

class StudentsCoursesBase(BaseModel):
    student_id: int
    course_id: int

class StudentsCoursesCreate(StudentsCoursesBase):
    pass

class StudentsCourses(StudentsCoursesBase):
     class Config:
        orm_mode = True
        from_attributes = True

class AttendanceBase(BaseModel):
    course_id: int
    student_id: int
    class_date: date # Use date type
    class_start_time: time # Use time type
    class_end_time: time # Use time type
    attendance_status: str # e.g., 'Present', 'Absent', 'Late'

class AttendanceCreate(AttendanceBase):
    pass

class Attendance(AttendanceBase):
    # No extra fields needed for reading based on current schema
     class Config:
        orm_mode = True
        from_attributes = True


# --- FastAPI App Instance ---
app = FastAPI()

# Run database initialization when the app starts
@app.on_event("startup")
async def startup_event():
    await init_db()

# --- CRUD Endpoints ---

# Students CRUD
@app.post("/students/", response_model=Student, status_code=status.HTTP_201_CREATED)
async def create_student(student: StudentCreate, db: aiosqlite.Connection = Depends(get_db)):
    # If using AUTOINCREMENT, omit student_id from INSERT and let DB handle it
    # If using manual IDs, add student_id to the model and INSERT statement
    # Using execute + fetchone to get the last ID
    cursor = await db.execute("SELECT student_id FROM students ORDER BY student_id DESC LIMIT 1")
    last_student_row = await cursor.fetchone()
    next_id = (last_student_row[0] + 1) if last_student_row and last_student_row[0] is not None else 1 # Simple auto-increment simulation if not using DB's AUTOINCREMENT, handle initial empty table

    try:
        await db.execute(
            "INSERT INTO students (student_id, student_name, student_age, student_email) VALUES (?, ?, ?, ?)",
            (next_id, student.student_name, student.student_age, student.student_email)
        )
        await db.commit()
        # Fetch the created student to return
        cursor = await db.execute("SELECT student_id, student_name, student_age, student_email FROM students WHERE student_id = ?", (next_id,))
        created_student_row = await cursor.fetchone()
        return dict(created_student_row) # Convert Row object to dictionary
    except aiosqlite.IntegrityError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error creating student: {e}")
    except Exception as e:
         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred: {e}")


@app.get("/students/", response_model=List[Student])
async def read_students(skip: int = 0, limit: int = 100, db: aiosqlite.Connection = Depends(get_db)):
    cursor = await db.execute("SELECT student_id, student_name, student_age, student_email FROM students LIMIT ? OFFSET ?", (limit, skip))
    students_rows = await cursor.fetchall()
    students = [dict(row) for row in students_rows] # Convert Row objects to dictionaries
    return students

@app.get("/students/{student_id}", response_model=Student)
async def read_student(student_id: int, db: aiosqlite.Connection = Depends(get_db)):
    cursor = await db.execute("SELECT student_id, student_name, student_age, student_email FROM students WHERE student_id = ?", (student_id,))
    student_row = await cursor.fetchone()
    if student_row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    return dict(student_row) # Convert Row object to dictionary

@app.put("/students/{student_id}", response_model=Student)
async def update_student(student_id: int, student: StudentCreate, db: aiosqlite.Connection = Depends(get_db)):
     try:
        cursor = await db.execute(
            "UPDATE students SET student_name = ?, student_age = ?, student_email = ? WHERE student_id = ?",
            (student.student_name, student.student_age, student.student_email, student_id)
        )
        await db.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
        # Fetch the updated student to return
        cursor = await db.execute("SELECT student_id, student_name, student_age, student_email FROM students WHERE student_id = ?", (student_id,))
        updated_student_row = await cursor.fetchone()
        return dict(updated_student_row) # Convert Row object to dictionary
     except aiosqlite.IntegrityError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error updating student: {e}")
     except Exception as e:
         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred: {e}")


@app.delete("/students/{student_id}", status_code=status.HTTP_200_OK)
async def delete_student(student_id: int, db: aiosqlite.Connection = Depends(get_db)):
    # Note: ON DELETE CASCADE in linking tables will handle related records
    cursor = await db.execute("DELETE FROM students WHERE student_id = ?", (student_id,))
    await db.commit()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    return {"detail": "Student deleted successfully"}

# Courses CRUD (Similar structure to Students)
@app.post("/courses/", response_model=Course, status_code=status.HTTP_201_CREATED)
async def create_course(course: CourseCreate, db: aiosqlite.Connection = Depends(get_db)):
    # Using execute + fetchone to get the last ID
    cursor = await db.execute("SELECT course_id FROM courses ORDER BY course_id DESC LIMIT 1")
    last_course_row = await cursor.fetchone()
    next_id = (last_course_row[0] + 1) if last_course_row and last_course_row[0] is not None else 1

    try:
        await db.execute("INSERT INTO courses (course_id, course_name) VALUES (?, ?)", (next_id, course.course_name))
        await db.commit()
        cursor = await db.execute("SELECT course_id, course_name FROM courses WHERE course_id = ?", (next_id,))
        created_course_row = await cursor.fetchone()
        return dict(created_course_row) # Convert Row object to dictionary
    except aiosqlite.IntegrityError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error creating course: {e}")
    except Exception as e:
         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred: {e}")


@app.get("/courses/", response_model=List[Course])
async def read_courses(skip: int = 0, limit: int = 100, db: aiosqlite.Connection = Depends(get_db)):
    cursor = await db.execute("SELECT course_id, course_name FROM courses LIMIT ? OFFSET ?", (limit, skip))
    courses_rows = await cursor.fetchall()
    courses = [dict(row) for row in courses_rows] # Convert Row objects to dictionaries
    return courses

@app.get("/courses/{course_id}", response_model=Course)
async def read_course(course_id: int, db: aiosqlite.Connection = Depends(get_db)):
    cursor = await db.execute("SELECT course_id, course_name FROM courses WHERE course_id = ?", (course_id,))
    course_row = await cursor.fetchone()
    if course_row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    return dict(course_row) # Convert Row object to dictionary

@app.put("/courses/{course_id}", response_model=Course)
async def update_course(course_id: int, course: CourseCreate, db: aiosqlite.Connection = Depends(get_db)):
    try:
        cursor = await db.execute("UPDATE courses SET course_name = ? WHERE course_id = ?", (course.course_name, course_id))
        await db.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
        cursor = await db.execute("SELECT course_id, course_name FROM courses WHERE course_id = ?", (course_id,))
        updated_course_row = await cursor.fetchone()
        return dict(updated_course_row) # Convert Row object to dictionary
    except aiosqlite.IntegrityError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error updating course: {e}")
    except Exception as e:
         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred: {e}")


@app.delete("/courses/{course_id}", status_code=status.HTTP_200_OK)
async def delete_course(course_id: int, db: aiosqlite.Connection = Depends(get_db)):
    cursor = await db.execute("DELETE FROM courses WHERE course_id = ?", (course_id,))
    await db.commit()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    return {"detail": "Course deleted successfully"}

# Teachers CRUD (Similar structure)
@app.post("/teachers/", response_model=Teacher, status_code=status.HTTP_201_CREATED)
async def create_teacher(teacher: TeacherCreate, db: aiosqlite.Connection = Depends(get_db)):
    # Using execute + fetchone to get the last ID
    cursor = await db.execute("SELECT teacher_id FROM teachers ORDER BY teacher_id DESC LIMIT 1")
    last_teacher_row = await cursor.fetchone()
    next_id = (last_teacher_row[0] + 1) if last_teacher_row and last_teacher_row[0] is not None else 1
    try:
        await db.execute(
            "INSERT INTO teachers (teacher_id, teacher_name, teacher_email) VALUES (?, ?, ?)",
            (next_id, teacher.teacher_name, teacher.teacher_email)
        )
        await db.commit()
        cursor = await db.execute("SELECT teacher_id, teacher_name, teacher_email FROM teachers WHERE teacher_id = ?", (next_id,))
        created_teacher_row = await cursor.fetchone()
        return dict(created_teacher_row) # Convert Row object to dictionary
    except aiosqlite.IntegrityError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error creating teacher: {e}")
    except Exception as e:
         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred: {e}")


@app.get("/teachers/", response_model=List[Teacher])
async def read_teachers(skip: int = 0, limit: int = 100, db: aiosqlite.Connection = Depends(get_db)):
    cursor = await db.execute("SELECT teacher_id, teacher_name, teacher_email FROM teachers LIMIT ? OFFSET ?", (limit, skip))
    teachers_rows = await cursor.fetchall()
    teachers = [dict(row) for row in teachers_rows] # Convert Row objects to dictionaries
    return teachers

@app.get("/teachers/{teacher_id}", response_model=Teacher)
async def read_teacher(teacher_id: int, db: aiosqlite.Connection = Depends(get_db)):
    cursor = await db.execute("SELECT teacher_id, teacher_name, teacher_email FROM teachers WHERE teacher_id = ?", (teacher_id,))
    teacher_row = await cursor.fetchone()
    if teacher_row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Teacher not found")
    return dict(teacher_row) # Convert Row object to dictionary

@app.put("/teachers/{teacher_id}", response_model=Teacher)
async def update_teacher(teacher_id: int, teacher: TeacherCreate, db: aiosqlite.Connection = Depends(get_db)):
     try:
        cursor = await db.execute(
            "UPDATE teachers SET teacher_name = ?, teacher_email = ? WHERE teacher_id = ?",
            (teacher.teacher_name, teacher.teacher_email, teacher_id)
        )
        await db.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Teacher not found")
        cursor = await db.execute("SELECT teacher_id, teacher_name, teacher_email FROM teachers WHERE teacher_id = ?", (teacher_id,))
        updated_teacher_row = await cursor.fetchone()
        return dict(updated_teacher_row) # Convert Row object to dictionary
     except aiosqlite.IntegrityError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error updating teacher: {e}")
     except Exception as e:
         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred: {e}")


@app.delete("/teachers/{teacher_id}", status_code=status.HTTP_200_OK)
async def delete_teacher(teacher_id: int, db: aiosqlite.Connection = Depends(get_db)):
    cursor = await db.execute("DELETE FROM teachers WHERE teacher_id = ?", (teacher_id,))
    await db.commit()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Teacher not found")
    return {"detail": "Teacher deleted successfully"}

# CourseTeacher Linking Table CRUD
@app.post("/course-teachers/", response_model=CourseTeacher, status_code=status.HTTP_201_CREATED)
async def link_course_teacher(link: CourseTeacherCreate, db: aiosqlite.Connection = Depends(get_db)):
    try:
        await db.execute(
            "INSERT INTO course_teacher (teacher_id, course_id) VALUES (?, ?)",
            (link.teacher_id, link.course_id)
        )
        await db.commit()
        # Return the created link object (no DB fetch needed as input matches output model)
        return link
    except aiosqlite.IntegrityError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error linking teacher to course (check if IDs exist or link already exists): {e}")
    except Exception as e:
         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred: {e}")

@app.get("/course-teachers/", response_model=List[CourseTeacher])
async def read_course_teachers(skip: int = 0, limit: int = 100, db: aiosqlite.Connection = Depends(get_db)):
    cursor = await db.execute("SELECT teacher_id, course_id FROM course_teacher LIMIT ? OFFSET ?", (limit, skip))
    links_rows = await cursor.fetchall()
    links = [dict(row) for row in links_rows] # Convert Row objects to dictionaries
    return links

# Note: Update is not typical for linking tables, delete and re-create is common

@app.delete("/course-teachers/{teacher_id}/{course_id}", status_code=status.HTTP_200_OK)
async def unlink_course_teacher(teacher_id: int, course_id: int, db: aiosqlite.Connection = Depends(get_db)):
    cursor = await db.execute(
        "DELETE FROM course_teacher WHERE teacher_id = ? AND course_id = ?",
        (teacher_id, course_id)
    )
    await db.commit()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course-Teacher link not found")
    return {"detail": "Course-Teacher link deleted successfully"}

# StudentsCourses Linking Table CRUD (Similar structure)
@app.post("/student-courses/", response_model=StudentsCourses, status_code=status.HTTP_201_CREATED)
async def link_student_course(link: StudentsCoursesCreate, db: aiosqlite.Connection = Depends(get_db)):
    try:
        await db.execute(
            "INSERT INTO students_courses (student_id, course_id) VALUES (?, ?)",
            (link.student_id, link.course_id)
        )
        await db.commit()
        return link
    except aiosqlite.IntegrityError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error enrolling student in course (check if IDs exist or enrollment already exists): {e}")
    except Exception as e:
         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred: {e}")

@app.get("/student-courses/", response_model=List[StudentsCourses])
async def read_student_courses(skip: int = 0, limit: int = 100, db: aiosqlite.Connection = Depends(get_db)):
    cursor = await db.execute("SELECT student_id, course_id FROM students_courses LIMIT ? OFFSET ?", (limit, skip))
    links_rows = await cursor.fetchall()
    links = [dict(row) for row in links_rows] # Convert Row objects to dictionaries
    return links

@app.delete("/student-courses/{student_id}/{course_id}", status_code=status.HTTP_200_OK)
async def unlink_student_course(student_id: int, course_id: int, db: aiosqlite.Connection = Depends(get_db)):
    cursor = await db.execute(
        "DELETE FROM students_courses WHERE student_id = ? AND course_id = ?",
        (student_id, course_id)
    )
    await db.commit()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student-Course link not found")
    return {"detail": "Student-Course link deleted successfully"}


# Attendance CRUD
@app.post("/attendance/", response_model=Attendance, status_code=status.HTTP_201_CREATED)
async def create_attendance(attendance: AttendanceCreate, db: aiosqlite.Connection = Depends(get_db)):
    try:
        await db.execute(
            "INSERT INTO attendance (course_id, student_id, class_date, class_start_time, class_end_time, attendance_status) VALUES (?, ?, ?, ?, ?, ?)",
            (
                attendance.course_id,
                attendance.student_id,
                attendance.class_date.isoformat(), # Convert date to string
                attendance.class_start_time.isoformat(), # Convert time to string
                attendance.class_end_time.isoformat(), # Convert time to string
                attendance.attendance_status
            )
        )
        await db.commit()
         # Fetch the created attendance record to return
        cursor = await db.execute(
            "SELECT course_id, student_id, class_date, class_start_time, class_end_time, attendance_status FROM attendance WHERE course_id = ? AND student_id = ? AND class_date = ? AND class_start_time = ?",
            (
                attendance.course_id,
                attendance.student_id,
                attendance.class_date.isoformat(), # Use string format for lookup
                attendance.class_start_time.isoformat() # Use string format for lookup
            )
        )
        created_attendance_row = await cursor.fetchone()
        # The fetched data will have date/time as strings, Pydantic with from_attributes=True should handle parsing back
        return dict(created_attendance_row) # Convert Row object to dictionary
    except aiosqlite.IntegrityError as e:
        # Check if the error is due to a duplicate primary key
        if "UNIQUE constraint failed" in str(e):
             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Attendance record for this student, course, date, and start time already exists.")
        # Check if the error is due to a foreign key constraint (including the new one)
        if "FOREIGN KEY constraint failed" in str(e):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid course_id or student_id, or student is not enrolled in this course: {e}")
        # Other integrity errors
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error creating attendance record: {e}")
    except Exception as e:
         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred: {e}")


@app.get("/attendance/", response_model=List[Attendance])
async def read_attendance(
    course_id: Optional[int] = None, # Optional query parameter to filter by course
    student_id: Optional[int] = None, # Optional query parameter to filter by student
    skip: int = 0,
    limit: int = 100,
    db: aiosqlite.Connection = Depends(get_db)
):
    query = "SELECT course_id, student_id, class_date, class_start_time, class_end_time, attendance_status FROM attendance WHERE 1=1"
    params = []

    if course_id is not None:
        query += " AND course_id = ?"
        params.append(course_id)
    if student_id is not None:
        query += " AND student_id = ?"
        params.append(student_id)

    query += " LIMIT ? OFFSET ?"
    params.extend([limit, skip])

    cursor = await db.execute(query, tuple(params))
    records_rows = await cursor.fetchall()
    records = [dict(row) for row in records_rows] # Convert Row objects to dictionaries
    return records


@app.get("/attendance/record/", response_model=Attendance)
async def read_attendance_record(
    course_id: int,
    student_id: int,
    class_date: date, # Pydantic will parse this from query string
    class_start_time: time, # Pydantic will parse this from query string
    db: aiosqlite.Connection = Depends(get_db)
):
    # Convert input date/time objects from path/query to strings for SQLite query
    cursor = await db.execute(
        "SELECT course_id, student_id, class_date, class_start_time, class_end_time, attendance_status FROM attendance WHERE course_id = ? AND student_id = ? AND class_date = ? AND class_start_time = ?",
        (
            course_id,
            student_id,
            class_date.isoformat(), # Convert date to string for query
            class_start_time.isoformat() # Convert time to string for query
        )
    )
    record_row = await cursor.fetchone()
    if record_row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attendance record not found")
     # The fetched data will have date/time as strings, Pydantic with from_attributes=True should handle parsing back
    return dict(record_row) # Convert Row object to dictionary

@app.put("/attendance/record/", response_model=Attendance)
async def update_attendance_record(
    course_id: int,
    student_id: int,
    class_date: date, # Pydantic will parse from query string
    class_start_time: time, # Pydantic will parse from query string
    attendance: AttendanceCreate, # Use Create model for update payload
    db: aiosqlite.Connection = Depends(get_db)
):
    # Ensure the update applies to the correct record by its PK (using string formats)
    # And update the modifiable fields (end_time, status) using string formats
    try:
        cursor = await db.execute(
            """
            UPDATE attendance
            SET class_end_time = ?, attendance_status = ?
            WHERE course_id = ? AND student_id = ? AND class_date = ? AND class_start_time = ?
            """,
            (
                attendance.class_end_time.isoformat(), # Convert time to string for update
                attendance.attendance_status,
                course_id,
                student_id,
                class_date.isoformat(), # Convert date to string for WHERE clause
                class_start_time.isoformat() # Convert time to string for WHERE clause
            )
        )
        await db.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attendance record not found")

        # Fetch the updated record to return
        cursor = await db.execute(
             "SELECT course_id, student_id, class_date, class_start_time, class_end_time, attendance_status FROM attendance WHERE course_id = ? AND student_id = ? AND class_date = ? AND class_start_time = ?",
            (course_id, student_id, class_date.isoformat(), class_start_time.isoformat()) # Use string formats for lookup
        )
        updated_record_row = await cursor.fetchone()
         # The fetched data will have date/time as strings, Pydantic with from_attributes=True should handle parsing back
        return dict(updated_record_row) # Convert Row object to dictionary

    except aiosqlite.IntegrityError as e:
         # Check if the error is due to a foreign key constraint (including the new one)
        if "FOREIGN KEY constraint failed" in str(e):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid course_id or student_id, or student is not enrolled in this course: {e}")
        # Other integrity errors
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error updating attendance record: {e}")
    except Exception as e:
         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred: {e}")


@app.delete("/attendance/record/", status_code=status.HTTP_200_OK)
async def delete_attendance_record(
    course_id: int,
    student_id: int,
    class_date: date, # Pydantic will parse from query string
    class_start_time: time, # Pydantic will parse from query string
    db: aiosqlite.Connection = Depends(get_db)
):
    # Convert input date/time objects from path/query to strings for SQLite query
    cursor = await db.execute(
        "DELETE FROM attendance WHERE course_id = ? AND student_id = ? AND class_date = ? AND class_start_time = ?",
        (course_id, student_id, class_date.isoformat(), class_start_time.isoformat()) # Convert date/time to strings for query
    )
    await db.commit()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attendance record not found")
    return {"detail": "Attendance record deleted successfully"}

# You can add more complex queries and endpoints as needed,
# e.g., get courses for a student, get students for a course, get teacher's courses etc.