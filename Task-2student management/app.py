import os
import re
from datetime import date, datetime

import mysql.connector
from flask import Flask, jsonify, request
from flask_cors import CORS
from mysql.connector import Error, IntegrityError


app = Flask(__name__, static_folder="static", static_url_path="")
CORS(app)

DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "Sathis@2002",
    "database": "student_management",
}


def get_db():
    return mysql.connector.connect(**DB_CONFIG)


def student_to_json(student):
    for key, value in student.items():
        if isinstance(value, (date, datetime)):
            student[key] = value.isoformat()
    return student


def validate_student(payload):
    if not isinstance(payload, dict):
        return None, "A JSON request body is required."

    fields = {name: str(payload.get(name, "")).strip() for name in ("full_name", "email", "phone", "course")}
    labels = {"full_name": "Full name", "email": "Email", "phone": "Phone", "course": "Course"}
    for field, value in fields.items():
        if not value:
            return None, f"{labels[field]} is required."

    if len(fields["full_name"]) > 100 or len(fields["email"]) > 100 or len(fields["course"]) > 50:
        return None, "One or more fields exceed the allowed length."
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", fields["email"]):
        return None, "Please provide a valid email address."
    if not re.fullmatch(r"[0-9+()\-\s]{7,15}", fields["phone"]):
        return None, "Phone must contain 7 to 15 valid phone characters."
    return fields, None


@app.get("/")
def index():
    return app.send_static_file("index.html")


@app.get("/api/students")
def list_students():
    try:
        with get_db() as db, db.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT id, full_name, email, phone, course, enrolled_on FROM students ORDER BY id DESC")
            return jsonify([student_to_json(row) for row in cursor.fetchall()])
    except Error:
        return jsonify(error="Database connection failed. Check your MySQL settings."), 503


@app.get("/api/students/search")
def search_students():
    query = request.args.get("q", "").strip()
    if len(query) > 100:
        return jsonify(error="Search query is too long."), 400
    try:
        with get_db() as db, db.cursor(dictionary=True) as cursor:
            term = f"%{query}%"
            cursor.execute(
                "SELECT id, full_name, email, phone, course, enrolled_on FROM students "
                "WHERE full_name LIKE %s OR course LIKE %s ORDER BY id DESC",
                (term, term),
            )
            return jsonify([student_to_json(row) for row in cursor.fetchall()])
    except Error:
        return jsonify(error="Database connection failed. Check your MySQL settings."), 503


@app.post("/api/students")
def create_student():
    student, error = validate_student(request.get_json(silent=True))
    if error:
        return jsonify(error=error), 400
    try:
        with get_db() as db, db.cursor(dictionary=True) as cursor:
            cursor.execute(
                "INSERT INTO students (full_name, email, phone, course) VALUES (%s, %s, %s, %s)",
                (student["full_name"], student["email"], student["phone"], student["course"]),
            )
            student_id = cursor.lastrowid
            db.commit()
            cursor.execute("SELECT id, full_name, email, phone, course, enrolled_on FROM students WHERE id = %s", (student_id,))
            return jsonify(student_to_json(cursor.fetchone())), 201
    except IntegrityError:
        return jsonify(error="A student with this email already exists."), 409
    except Error:
        return jsonify(error="Database connection failed. Check your MySQL settings."), 503


@app.put("/api/students/<int:student_id>")
def update_student(student_id):
    student, error = validate_student(request.get_json(silent=True))
    if error:
        return jsonify(error=error), 400
    try:
        with get_db() as db, db.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT id FROM students WHERE id = %s", (student_id,))
            if not cursor.fetchone():
                return jsonify(error="Student not found."), 404
            cursor.execute(
                "UPDATE students SET full_name = %s, email = %s, phone = %s, course = %s WHERE id = %s",
                (student["full_name"], student["email"], student["phone"], student["course"], student_id),
            )
            db.commit()
            cursor.execute("SELECT id, full_name, email, phone, course, enrolled_on FROM students WHERE id = %s", (student_id,))
            return jsonify(student_to_json(cursor.fetchone()))
    except IntegrityError:
        return jsonify(error="A student with this email already exists."), 409
    except Error:
        return jsonify(error="Database connection failed. Check your MySQL settings."), 503


@app.delete("/api/students/<int:student_id>")
def delete_student(student_id):
    try:
        with get_db() as db, db.cursor() as cursor:
            cursor.execute("DELETE FROM students WHERE id = %s", (student_id,))
            if cursor.rowcount == 0:
                return jsonify(error="Student not found."), 404
            db.commit()
            return jsonify(message="Student deleted successfully.")
    except Error:
        return jsonify(error="Database connection failed. Check your MySQL settings."), 503


if __name__ == "__main__":
    app.run(debug=True)
