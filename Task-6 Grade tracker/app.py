"""Student Marks & Grade Tracker REST API."""
import os
from decimal import Decimal, InvalidOperation

from flask import Flask, jsonify, request
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error, IntegrityError
from werkzeug.exceptions import HTTPException

app = Flask(__name__)
CORS(app)

DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "Sathis@2002",
    "database": "grade_tracker"
}

GRADE_REMARKS = {
    "A": "Outstanding", "B": "Well done", "C": "Keep improving",
    "D": "Needs attention", "F": "Please seek help",
}


def calculate_grade(percentage):
    """Return a letter grade for a percentage. Grade logic lives only here."""
    percentage = float(percentage)
    if percentage >= 90:
        return "A"
    if percentage >= 75:
        return "B"
    if percentage >= 60:
        return "C"
    if percentage >= 45:
        return "D"
    return "F"


def db_connection():
    return mysql.connector.connect(**DB_CONFIG)


def query(sql, params=(), *, one=False, commit=False):
    """Run a parameterised query and always close its database resources."""
    connection = db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(sql, params)
        if commit:
            connection.commit()
            return cursor.lastrowid, cursor.rowcount
        rows = cursor.fetchall()
        return (rows[0] if rows else None) if one else rows
    finally:
        cursor.close()
        connection.close()


def payload():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise ValueError("Request body must be a JSON object")
    return data


def require_text(data, field):
    value = data.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"'{field}' is required and must be a non-empty string")
    return value.strip()


def number(value, field):
    if isinstance(value, bool):
        raise ValueError(f"'{field}' must be a number")
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError(f"'{field}' must be a number")


def student_or_404(student_id):
    student = query("SELECT id, name, email, created_at FROM students WHERE id = %s", (student_id,), one=True)
    if not student:
        return None
    return serialize_student(student)


def serialize_student(student):
    student["created_at"] = student["created_at"].isoformat() if student.get("created_at") else None
    return student


def serialize_mark(mark):
    score = float(mark["score"])
    max_score = float(mark["max_score"])
    percentage = round((score / max_score) * 100, 2)
    grade = calculate_grade(percentage)
    return {
        "id": mark["id"], "student_id": mark["student_id"], "subject": mark["subject"],
        "score": score, "max_score": max_score, "percentage": percentage,
        "grade": grade, "remarks": GRADE_REMARKS[grade],
        "added_on": mark["added_on"].isoformat() if mark.get("added_on") else None,
    }


@app.errorhandler(ValueError)
def handle_bad_input(error):
    return jsonify(error=str(error)), 400


@app.errorhandler(IntegrityError)
def handle_integrity_error(error):
    return jsonify(error="Email address already exists"), 409


@app.errorhandler(Error)
def handle_database_error(error):
    app.logger.exception("Database error: %s", error)
    return jsonify(error="Unable to process the database request"), 400


@app.errorhandler(Exception)
def handle_unexpected_error(error):
    # Preserve Flask/Werkzeug HTTP status codes (for example, unknown URLs).
    if isinstance(error, HTTPException):
        return jsonify(error=error.description), error.code
    app.logger.exception("Unexpected error: %s", error)
    return jsonify(error="Unable to process the request"), 400


@app.get("/")
def index():
    return jsonify(message="Student Marks & Grade Tracker API", status="running")


@app.get("/students")
def list_students():
    students = query("SELECT id, name, email, created_at FROM students ORDER BY id")
    return jsonify(students=[serialize_student(s) for s in students])


@app.get("/students/search")
def search_students():
    name = request.args.get("name", "").strip()
    if not name:
        raise ValueError("Query parameter 'name' is required")
    students = query("SELECT id, name, email, created_at FROM students WHERE name LIKE %s ORDER BY name", (f"%{name}%",))
    return jsonify(students=[serialize_student(s) for s in students])


@app.post("/students")
def create_student():
    data = payload()
    name, email = require_text(data, "name"), require_text(data, "email")
    student_id, _ = query("INSERT INTO students (name, email) VALUES (%s, %s)", (name, email), commit=True)
    return jsonify(message="Student created", student=student_or_404(student_id)), 201


@app.get("/students/<int:student_id>")
def get_student(student_id):
    student = student_or_404(student_id)
    if not student:
        return jsonify(error="Student not found"), 404
    return jsonify(student=student)


@app.put("/students/<int:student_id>")
def update_student(student_id):
    if not student_or_404(student_id):
        return jsonify(error="Student not found"), 404
    data = payload()
    updates, values = [], []
    for field in ("name", "email"):
        if field in data:
            updates.append(f"{field} = %s")
            values.append(require_text(data, field))
    if not updates:
        raise ValueError("Provide at least one of: name, email")
    values.append(student_id)
    query(f"UPDATE students SET {', '.join(updates)} WHERE id = %s", tuple(values), commit=True)
    return jsonify(message="Student updated", student=student_or_404(student_id))


@app.delete("/students/<int:student_id>")
def delete_student(student_id):
    _, count = query("DELETE FROM students WHERE id = %s", (student_id,), commit=True)
    if not count:
        return jsonify(error="Student not found"), 404
    return jsonify(message="Student and all associated marks deleted")


@app.get("/students/<int:student_id>/marks")
def get_marks(student_id):
    if not student_or_404(student_id):
        return jsonify(error="Student not found"), 404
    subject = request.args.get("subject", "").strip()
    sql, params = "SELECT * FROM marks WHERE student_id = %s", [student_id]
    if subject:
        sql += " AND subject LIKE %s"
        params.append(f"%{subject}%")
    sql += " ORDER BY added_on, id"
    marks = query(sql, tuple(params))
    return jsonify(student_id=student_id, marks=[serialize_mark(m) for m in marks])


@app.post("/students/<int:student_id>/marks")
def add_mark(student_id):
    if not student_or_404(student_id):
        return jsonify(error="Student not found"), 404
    data = payload()
    subject = require_text(data, "subject")
    score = number(data.get("score"), "score")
    max_score = number(data.get("max_score", 100), "max_score")
    if max_score <= 0:
        raise ValueError("'max_score' must be greater than zero")
    if score < 0 or score > max_score:
        raise ValueError("'score' must be between 0 and max_score")
    mark_id, _ = query("INSERT INTO marks (student_id, subject, score, max_score) VALUES (%s, %s, %s, %s)",
                       (student_id, subject, score, max_score), commit=True)
    mark = query("SELECT * FROM marks WHERE id = %s", (mark_id,), one=True)
    return jsonify(message="Mark added", mark=serialize_mark(mark)), 201


@app.delete("/marks/<int:mark_id>")
def delete_mark(mark_id):
    _, count = query("DELETE FROM marks WHERE id = %s", (mark_id,), commit=True)
    if not count:
        return jsonify(error="Mark not found"), 404
    return jsonify(message="Mark deleted")


def student_average(student_id):
    row = query("SELECT AVG((score / max_score) * 100) AS average_percentage FROM marks WHERE student_id = %s", (student_id,), one=True)
    return round(float(row["average_percentage"]), 2) if row and row["average_percentage"] is not None else None


@app.get("/students/<int:student_id>/report")
def student_report(student_id):
    student = student_or_404(student_id)
    if not student:
        return jsonify(error="Student not found"), 404
    marks = [serialize_mark(m) for m in query("SELECT * FROM marks WHERE student_id = %s ORDER BY subject", (student_id,))]
    average = student_average(student_id)
    if average is None:
        return jsonify(student=student, subjects=[], average_percentage=None, overall_grade=None,
                       status="No marks available", best_subject=None, weakest_subject=None)
    return jsonify(student=student, subjects=marks, average_percentage=average,
                   overall_grade=calculate_grade(average), status="Pass" if average >= 45 else "Fail",
                   best_subject=max(marks, key=lambda m: m["percentage"]),
                   weakest_subject=min(marks, key=lambda m: m["percentage"]))


@app.get("/summary")
def class_summary():
    students = query("SELECT id, name, email FROM students ORDER BY id")
    ranked = []
    for student in students:
        average = student_average(student["id"])
        if average is not None:
            ranked.append({"id": student["id"], "name": student["name"], "average_percentage": average,
                           "grade": calculate_grade(average)})
    ranked.sort(key=lambda s: s["average_percentage"], reverse=True)
    for rank, student in enumerate(ranked, 1):
        student["rank"] = rank
    grades = {grade: 0 for grade in "ABCDF"}
    for student in ranked:
        grades[student["grade"]] += 1
    # This averages every recorded subject percentage across the class.
    class_average_row = query(
        "SELECT AVG((score / max_score) * 100) AS class_average_percentage FROM marks",
        one=True,
    )
    raw_class_average = class_average_row["class_average_percentage"]
    class_average = round(float(raw_class_average), 2) if raw_class_average is not None else None
    return jsonify(total_students=len(students), class_average_percentage=class_average,
                   students_per_grade=grades, highest_scoring_student=ranked[0] if ranked else None,
                   lowest_scoring_student=ranked[-1] if ranked else None,
                   pass_count=sum(s["grade"] != "F" for s in ranked), fail_count=grades["F"], rankings=ranked)


if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG", "false").lower() == "true", host="0.0.0.0", port=5000)
