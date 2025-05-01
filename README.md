# Student Records API

## Project Title

Student Records API

## Description

This project implements a simple RESTful API for managing student records, courses, teachers, and attendance. It is built using the **FastAPI** web framework in Python and uses **SQLite** as the database engine. The API provides standard Create, Read, Update, and Delete (CRUD) operations for each resource, allowing you to manage your student database programmatically.

The database schema is defined in the [students_records SQL File](https://github.com/ntaboisoe/student-DB/blob/main/students_records%20SQL%20File.sql) and visualized in the [Student Records ERD](https://github.com/ntaboisoe/student-DB/blob/main/student_records%20ERD%20File.gif). You can use the SQL file to manually recreate the database schema and initial data if needed, although the API will create it automatically on the first run if the database file is not found.

## How to Run/Set Up the Project

These instructions assume you have Python and Anaconda installed on your system.

1.  **Save the Code:**
    Save the provided Python code for the FastAPI application into a file named `main.py` in your project directory. Ensure this directory is where you want the `student_records.db` file to be located, or update the `DATABASE_URL` in `main.py` to point to your desired location.

2.  **Open Your Terminal/Anaconda Prompt:**
    Launch your Anaconda Prompt or a terminal where your Python environment is activated.

3.  **Navigate to the Project Directory:**
    Use the `cd` command to go to the directory where you saved `main.py`.
    ```bash
    cd path/to/your/project
    ```

4.  **Install Dependencies:**
    Install the necessary Python packages using pip:
    ```bash
    pip install fastapi uvicorn aiosqlite
    ```
    * `fastapi`: The web framework.
    * `uvicorn`: The ASGI server that runs your FastAPI application.
    * `aiosqlite`: An asynchronous driver for SQLite databases, allowing non-blocking database operations with FastAPI.

5.  **Database Setup:**
    SQLite is the database engine. The application is configured to use a database file named `student_records.db`.
    * **Automatic Creation:** On the **first run** of the application (if `student_records.db` does not exist in the specified location), the `init_db()` function will automatically create the database file, set up the schema as defined in the `schema_sql` string within `main.py`, and populate it with sample data from the `insert_sql` string.
    * **Manual Creation:** Alternatively, you can manually create and populate the database by executing the SQL commands from the [students_records SQL File](https://github.com/ntaboisoe/student-DB/blob/main/students_records%20SQL%20File.sql) using a SQLite client (like the `sqlite3` command-line tool or DBeaver) before running the API.

6.  **Run the Application:**
    Execute the following command in your terminal from the project directory:
    ```bash
    uvicorn main:app --reload
    ```
    * `main`: Refers to the `main.py` file.
    * `app`: Refers to the `FastAPI()` instance within `main.py`.
    * `--reload`: Restarts the server automatically when you make changes to the code (useful during development).

7.  **Access the API:**
    The API will be running locally, typically at `http://127.0.0.1:8000`.

## How to Use the API

FastAPI automatically generates interactive API documentation based on your code. This is the easiest way to explore and test the endpoints:

1.  Open your web browser and go to `http://127.0.0.1:8000/docs`. This will show the **Swagger UI**.
2.  Alternatively, you can visit `http://127.0.0.1:8000/redoc` for a different documentation style.

The documentation provides details on:

* All available endpoints (e.g., `/students/`, `/courses/`, `/teachers/`, `/attendance/`, `/course-teachers/`, `/student-courses/`).
* The required HTTP method for each endpoint (GET, POST, PUT, DELETE).
* Expected request body format (for POST and PUT requests).
* Expected response format for each endpoint.
* You can directly interact with the API from the Swagger UI to test creating, reading, updating, and deleting records.

**Example Endpoints:**

* `GET /students/`: Retrieve a list of all students.
* `POST /students/`: Create a new student record.
* `GET /students/{student_id}`: Retrieve a specific student by ID.
* `PUT /students/{student_id}`: Update a specific student record.
* `DELETE /students/{student_id}`: Delete a specific student record.
* ... and similar endpoints for courses, teachers, and the linking/attendance tables.

## Acknowledgments

* **[Robert Isoe](https://github.com/ntaboisoe)**: Initial schema design and project concept.
* **Gemini**: Assistance with schema validation and improvements, generating sample data, developing the FastAPI application code, and debugging.
