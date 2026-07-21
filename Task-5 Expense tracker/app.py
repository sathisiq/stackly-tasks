import os
from datetime import datetime
from decimal import Decimal, InvalidOperation
from functools import wraps

import mysql.connector
from flask import Flask, jsonify, request, send_from_directory, session
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from mysql.connector import Error
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__, static_folder="static")
app.config.update(
    SECRET_KEY=os.getenv("SECRET_KEY", "change-this-secret-before-production"),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
)
CORS(app, supports_credentials=True)
bcrypt = Bcrypt(app)

CATEGORIES = {"Food", "Transport", "Shopping", "Health", "Education", "Entertainment", "Other"}


def db_connection():
    return mysql.connector.connect(
        host="localhost",
        port=3306,
        user="root",
        password="Sathis@2002",  
        database="expense_tracker"
    )


def database_error(error):
    app.logger.exception("Database error: %s", error)
    return jsonify(error="Database connection failed. Check your MySQL configuration."), 500


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            return jsonify(error="Authentication required."), 401
        return view(*args, **kwargs)
    return wrapped


def payload():
    return request.get_json(silent=True) or {}


def validate_expense(data):
    title = str(data.get("title", "")).strip()
    category = str(data.get("category", "")).strip()
    note = str(data.get("note", "")).strip()
    date_text = str(data.get("date", "")).strip()
    if not title or len(title) > 100:
        return None, "Title is required and must be at most 100 characters."
    if category not in CATEGORIES:
        return None, "Choose a valid category."
    if len(note) > 255:
        return None, "Note must be at most 255 characters."
    try:
        amount = Decimal(str(data.get("amount", "")))
        if not amount.is_finite() or amount <= 0 or amount > Decimal("99999999.99"):
            raise InvalidOperation
    except (InvalidOperation, ValueError):
        return None, "Amount must be a positive number."
    try:
        datetime.strptime(date_text, "%Y-%m-%d")
    except ValueError:
        return None, "Date must use YYYY-MM-DD format."
    return (title, amount, category, date_text, note or None), None


def serialize_expense(row):
    item = dict(row)
    item["amount"] = float(item["amount"])
    item["date"] = item["date"].isoformat()
    if item.get("created_at"):
        item["created_at"] = item["created_at"].isoformat()
    return item


@app.get("/")
def index():
    return send_from_directory(app.static_folder, "login.html")


@app.get("/<path:filename>")
def static_pages(filename):
    allowed = {"login.html", "register.html", "dashboard.html", "expenses.html"}
    if filename in allowed:
        return send_from_directory(app.static_folder, filename)
    return jsonify(error="Not found."), 404


@app.post("/register")
def register():
    data = payload()
    username, email, password = (str(data.get(k, "")).strip() for k in ("username", "email", "password"))
    if not 3 <= len(username) <= 50 or not email or len(email) > 100 or len(password) < 6:
        return jsonify(error="Username (3-50), email, and password (at least 6 characters) are required."), 400
    try:
        conn = db_connection(); cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                       (username, email.lower(), bcrypt.generate_password_hash(password).decode("utf-8")))
        conn.commit()
        return jsonify(message="Registration successful. Please log in."), 201
    except Error as error:
        if getattr(error, "errno", None) == 1062:
            return jsonify(error="Username or email is already registered."), 400
        return database_error(error)
    finally:
        if "cursor" in locals(): cursor.close()
        if "conn" in locals() and conn.is_connected(): conn.close()


@app.post("/login")
def login():
    data = payload(); identity = str(data.get("identity", "")).strip(); password = str(data.get("password", ""))
    if not identity or not password:
        return jsonify(error="Username/email and password are required."), 400
    try:
        conn = db_connection(); cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, username, password FROM users WHERE username = %s OR email = %s", (identity, identity.lower()))
        user = cursor.fetchone()
        if not user or not bcrypt.check_password_hash(user["password"], password):
            return jsonify(error="Invalid username/email or password."), 401
        session.clear(); session["user_id"] = user["id"]; session["username"] = user["username"]
        return jsonify(message="Logged in.", user={"id": user["id"], "username": user["username"]})
    except Error as error:
        return database_error(error)
    finally:
        if "cursor" in locals(): cursor.close()
        if "conn" in locals() and conn.is_connected(): conn.close()


@app.get("/logout")
def logout():
    session.clear()
    return jsonify(message="Logged out.")


@app.get("/me")
@login_required
def me():
    return jsonify(user={"id": session["user_id"], "username": session["username"]})


@app.route("/expenses", methods=["GET", "POST"])
@login_required
def expenses():
    user_id = session["user_id"]
    try:
        conn = db_connection(); cursor = conn.cursor(dictionary=True)
        if request.method == "GET":
            cursor.execute("SELECT id, title, amount, category, date, note, created_at FROM expenses WHERE user_id = %s ORDER BY date DESC, id DESC", (user_id,))
            return jsonify(expenses=[serialize_expense(row) for row in cursor.fetchall()])
        values, error = validate_expense(payload())
        if error: return jsonify(error=error), 400
        cursor.execute("INSERT INTO expenses (user_id, title, amount, category, date, note) VALUES (%s, %s, %s, %s, %s, %s)", (user_id, *values))
        conn.commit()
        return jsonify(message="Expense added.", id=cursor.lastrowid), 201
    except Error as error:
        return database_error(error)
    finally:
        if "cursor" in locals(): cursor.close()
        if "conn" in locals() and conn.is_connected(): conn.close()


@app.route("/expenses/<int:expense_id>", methods=["PUT", "DELETE"])
@login_required
def expense_detail(expense_id):
    user_id = session["user_id"]
    try:
        conn = db_connection(); cursor = conn.cursor()
        if request.method == "DELETE":
            cursor.execute("DELETE FROM expenses WHERE id = %s AND user_id = %s", (expense_id, user_id))
        else:
            values, error = validate_expense(payload())
            if error: return jsonify(error=error), 400
            cursor.execute("UPDATE expenses SET title=%s, amount=%s, category=%s, date=%s, note=%s WHERE id=%s AND user_id=%s", (*values, expense_id, user_id))
        if cursor.rowcount == 0:
            return jsonify(error="Expense not found."), 404
        conn.commit()
        return jsonify(message="Expense deleted." if request.method == "DELETE" else "Expense updated.")
    except Error as error:
        return database_error(error)
    finally:
        if "cursor" in locals(): cursor.close()
        if "conn" in locals() and conn.is_connected(): conn.close()


@app.get("/expenses/summary")
@login_required
def summary():
    try:
        conn = db_connection(); cursor = conn.cursor(dictionary=True); user_id = session["user_id"]
        cursor.execute("SELECT COALESCE(SUM(amount), 0) AS total_amount, COUNT(*) AS expense_count, COALESCE(MAX(amount), 0) AS highest_expense, COUNT(DISTINCT category) AS category_count FROM expenses WHERE user_id = %s", (user_id,))
        totals = cursor.fetchone(); cursor.execute("SELECT category, SUM(amount) AS amount FROM expenses WHERE user_id = %s GROUP BY category ORDER BY amount DESC", (user_id,))
        totals.update({k: float(totals[k]) if isinstance(totals[k], Decimal) else totals[k] for k in ("total_amount", "highest_expense")})
        return jsonify(**totals, by_category=[{"category": row["category"], "amount": float(row["amount"])} for row in cursor.fetchall()])
    except Error as error:
        return database_error(error)
    finally:
        if "cursor" in locals(): cursor.close()
        if "conn" in locals() and conn.is_connected(): conn.close()


@app.get("/expenses/filter")
@login_required
def filter_expenses():
    category, date_from, date_to = request.args.get("category", ""), request.args.get("from", ""), request.args.get("to", "")
    if category and category not in CATEGORIES: return jsonify(error="Choose a valid category."), 400
    for value in (date_from, date_to):
        if value:
            try: datetime.strptime(value, "%Y-%m-%d")
            except ValueError: return jsonify(error="Dates must use YYYY-MM-DD format."), 400
    query = "SELECT id, title, amount, category, date, note, created_at FROM expenses WHERE user_id = %s"; params = [session["user_id"]]
    if category: query += " AND category = %s"; params.append(category)
    if date_from: query += " AND date >= %s"; params.append(date_from)
    if date_to: query += " AND date <= %s"; params.append(date_to)
    try:
        conn = db_connection(); cursor = conn.cursor(dictionary=True); cursor.execute(query + " ORDER BY date DESC, id DESC", params)
        return jsonify(expenses=[serialize_expense(row) for row in cursor.fetchall()])
    except Error as error:
        return database_error(error)
    finally:
        if "cursor" in locals(): cursor.close()
        if "conn" in locals() and conn.is_connected(): conn.close()


if __name__ == "__main__":
    app.run(debug=True)
