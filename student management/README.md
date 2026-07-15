# Student Management System

A Full Stack Student Management System built using **Python, Flask, MySQL, HTML, CSS, and JavaScript**. The application allows users to add, view, edit, delete, and search student records. All data is stored permanently in a MySQL database.

---

## Technologies Used

- Python
- Flask
- MySQL
- HTML
- CSS
- JavaScript

---

## Project Structure

```
student-management/
│
├── app.py
├── requirements.txt
├── database.sql
├── README.md
│
└── static/
    ├── index.html
    ├── style.css
    └── script.js
```

---

## Database Setup

Open MySQL Workbench and execute the following SQL commands:

```sql
CREATE DATABASE student_management;

USE student_management;

CREATE TABLE students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(15) NOT NULL,
    course VARCHAR(50) NOT NULL,
    enrolled_on DATE NOT NULL DEFAULT (CURRENT_DATE)
);
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

or

```bash
pip install flask flask-cors mysql-connector-python
```

---

## Configure Database

Update the MySQL connection details in `app.py`.

```python
DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "YOUR_MYSQL_PASSWORD",
    "database": "student_management",
}
```

Replace `YOUR_MYSQL_PASSWORD` with your MySQL password.

---

## Run the Application

```bash
python app.py
```

Open your browser:

```
http://localhost:5000
```

---

## REST API Endpoints

| Method | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/students` | Get all students |
| POST | `/api/students` | Add a new student |
| PUT | `/api/students/<id>` | Update student details |
| DELETE | `/api/students/<id>` | Delete a student |
| GET | `/api/students/search?q=value` | Search students by name or course |

---

## Features

- Add Student
- View Students
- Edit Student
- Delete Student with Confirmation
- Live Search
- Dashboard Statistics
- Responsive Design
- MySQL Database Storage
- REST API using Flask

---

## Notes

- Student data is stored permanently in MySQL.
- The frontend communicates with the backend using the Fetch API.
- No localStorage is used for storing student records.