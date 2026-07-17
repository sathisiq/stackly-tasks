import os
from datetime import timedelta
from functools import wraps

import mysql.connector
from flask import Flask, jsonify, redirect, request, send_from_directory, session
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_session import Session
from mysql.connector import Error, IntegrityError


app = Flask(__name__, static_folder="static")
app.config.update(
    SECRET_KEY=os.getenv("FLASK_SECRET_KEY", "change-this-development-secret-before-deploying"),
    SESSION_TYPE="filesystem",
    SESSION_FILE_DIR=os.path.join(app.root_path, ".flask_session"),
    SESSION_PERMANENT=False,
    SESSION_USE_SIGNER=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.getenv("FLASK_ENV") == "production",
    PERMANENT_SESSION_LIFETIME=timedelta(days=14),
)
Session(app)
bcrypt = Bcrypt(app)
CORS(app, supports_credentials=True)

DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "Sathis@2002",
    "database": "auth_system"
}


def db_connection():
    return mysql.connector.connect(**DB_CONFIG)


def api_error(message, status):
    return jsonify({"success": False, "message": message}), status


def protected_route(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            return api_error("Authentication required. Please log in.", 401)
        return view(*args, **kwargs)
    return wrapped


@app.get("/")
def index():
    return send_from_directory(app.static_folder, "login.html")


@app.get("/register.html")
def register_page():
    return send_from_directory(app.static_folder, "register.html")


@app.get("/dashboard.html")
def dashboard_page():
    return send_from_directory(app.static_folder, "dashboard.html")


@app.post("/register")
def register():
    data = request.get_json(silent=True) or {}
    username = str(data.get("username", "")).strip()
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))

    if not username or not email or not password:
        return api_error("Username, email, and password are required.", 400)
    if not 3 <= len(username) <= 50:
        return api_error("Username must be between 3 and 50 characters.", 400)
    if len(email) > 100 or "@" not in email:
        return api_error("Please provide a valid email address.", 400)
    if len(password) < 8:
        return api_error("Password must be at least 8 characters long.", 400)

    connection = cursor = None
    try:
        connection = db_connection()
        cursor = connection.cursor()
        password_hash = bcrypt.generate_password_hash(password).decode("utf-8")
        cursor.execute(
            "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
            (username, email, password_hash),
        )
        connection.commit()
        return jsonify({"success": True, "message": "Registration successful. Please log in."}), 201
    except IntegrityError as exc:
        if getattr(exc, "errno", None) == 1062:
            return api_error("That username or email is already registered.", 409)
        return api_error("Could not create the account.", 409)
    except Error:
        app.logger.exception("Database error during registration")
        return api_error("Database connection failed. Check the server configuration.", 500)
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


@app.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    username = str(data.get("username", "")).strip()
    password = str(data.get("password", ""))
    remember_me = bool(data.get("rememberMe", False))
    if not username or not password:
        return api_error("Username and password are required.", 400)

    connection = cursor = None
    try:
        connection = db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, username, email, password, role, created_at FROM users WHERE username = %s",
            (username,),
        )
        user = cursor.fetchone()
        if not user or not bcrypt.check_password_hash(user["password"], password):
            return api_error("Invalid username or password.", 401)

        session.clear()
        session["user_id"] = user["id"]
        session["username"] = user["username"]
        session["role"] = user["role"]
        session.permanent = remember_me
        return jsonify({"success": True, "message": "Login successful.", "username": user["username"], "role": user["role"]})
    except Error:
        app.logger.exception("Database error during login")
        return api_error("Database connection failed. Check the server configuration.", 500)
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


@app.get("/logout")
def logout():
    session.clear()
    return jsonify({"success": True, "message": "You have been logged out."})


@app.get("/dashboard")
@protected_route
def dashboard():
    connection = cursor = None
    try:
        connection = db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            "SELECT username, email, role, created_at FROM users WHERE id = %s", (session["user_id"],)
        )
        user = cursor.fetchone()
        if not user:
            session.clear()
            return api_error("User account no longer exists.", 401)
        user["created_at"] = user["created_at"].isoformat() if user["created_at"] else None
        return jsonify({"success": True, "user": user})
    except Error:
        app.logger.exception("Database error loading dashboard")
        return api_error("Database connection failed. Check the server configuration.", 500)
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

@app.get("/profile")
@protected_route
def profile():
    connection = cursor = None
    try:
        connection = db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            "SELECT username, email, role, created_at FROM users WHERE id = %s", (session["user_id"],)
        )
        user = cursor.fetchone()
        if not user:
            session.clear()
            return api_error("User account no longer exists.", 401)
        user["created_at"] = user["created_at"].isoformat() if user["created_at"] else None
        return jsonify({"success": True, "user": user})
    except Error:
        app.logger.exception("Database error loading profile")
        return api_error("Database connection failed. Check the server configuration.", 500)
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


if __name__ == "__main__":
    app.run(debug=True)
