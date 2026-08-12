import os
from datetime import date
from functools import wraps

import mysql.connector
from flask import Flask, jsonify, request, session
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from mysql.connector import Error

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'change-this-development-secret')
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
CORS(app, supports_credentials=True, origins=['http://localhost:5173'])
bcrypt = Bcrypt(app)

VALID_STATUSES = ['Applied', 'Shortlisted', 'Interview Scheduled', 'Offer Received', 'Rejected']


def get_db():
    return mysql.connector.connect(
        host=os.getenv('MYSQL_HOST', 'localhost'),
        user=os.getenv('MYSQL_USER', 'root'),
        password=os.getenv('MYSQL_PASSWORD', 'Sathis@2002'),
        database=os.getenv('MYSQL_DATABASE', 'job_tracker'),
    )


def protected_route(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return view(*args, **kwargs)
    return wrapped


def application_payload(data):
    required = ['company', 'role', 'applied_on']
    missing = [field for field in required if not str(data.get(field, '')).strip()]
    if missing:
        return None, f"Required fields missing: {', '.join(missing)}"
    status = data.get('status', 'Applied')
    if status not in VALID_STATUSES:
        return None, 'Invalid application status'
    try:
        date.fromisoformat(data['applied_on'])
    except (TypeError, ValueError):
        return None, 'Applied date must be YYYY-MM-DD'
    return {
        'company': data['company'].strip(), 'role': data['role'].strip(), 'status': status,
        'applied_on': data['applied_on'], 'location': data.get('location', '').strip() or None,
        'job_url': data.get('job_url', '').strip() or None, 'notes': data.get('notes', '').strip() or None,
    }, None


@app.errorhandler(Error)
def database_error(error):
    return jsonify({'error': 'Database error. Check your MySQL configuration.'}), 500


@app.post('/api/register')
def register():
    data = request.get_json(silent=True) or {}
    username, email, password = data.get('username', '').strip(), data.get('email', '').strip(), data.get('password', '')
    if not username or not email or not password:
        return jsonify({'error': 'Username, email and password are required'}), 400
    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400
    db = get_db(); cursor = db.cursor(dictionary=True)
    try:
        cursor.execute('SELECT id FROM users WHERE username = %s OR email = %s', (username, email))
        if cursor.fetchone():
            return jsonify({'error': 'Username or email is already registered'}), 409
        cursor.execute('INSERT INTO users (username, email, password) VALUES (%s, %s, %s)',
                       (username, email, bcrypt.generate_password_hash(password).decode('utf-8')))
        db.commit()
        return jsonify({'message': 'Registration successful'}), 201
    finally:
        cursor.close(); db.close()


@app.post('/api/login')
def login():
    data = request.get_json(silent=True) or {}
    username, password = data.get('username', '').strip(), data.get('password', '')
    db = get_db(); cursor = db.cursor(dictionary=True)
    try:
        cursor.execute('SELECT id, username, email, password FROM users WHERE username = %s', (username,))
        user = cursor.fetchone()
        if not user or not bcrypt.check_password_hash(user['password'], password):
            return jsonify({'error': 'Invalid username or password'}), 401
        session.clear(); session['user_id'] = user['id']; session['username'] = user['username']
        return jsonify({'user': {'id': user['id'], 'username': user['username'], 'email': user['email']}})
    finally:
        cursor.close(); db.close()


@app.get('/api/logout')
def logout():
    session.clear()
    return jsonify({'message': 'Logged out successfully'})


@app.get('/api/me')
def me():
    if 'user_id' not in session:
        # This endpoint is used by React during app startup to restore a session.
        # No active session is a normal state on the login/register pages.
        return jsonify({'user': None})
    return jsonify({'user': {'id': session['user_id'], 'username': session['username']}})


@app.route('/api/applications', methods=['GET', 'POST'])
@protected_route
def applications():
    db = get_db(); cursor = db.cursor(dictionary=True)
    try:
        if request.method == 'GET':
            cursor.execute("SELECT id, user_id, company, role, status, DATE_FORMAT(applied_on, '%Y-%m-%d') AS applied_on, location, job_url, notes, updated_at FROM applications WHERE user_id = %s ORDER BY applied_on DESC, id DESC", (session['user_id'],))
            return jsonify({'applications': cursor.fetchall()})
        payload, error = application_payload(request.get_json(silent=True) or {})
        if error: return jsonify({'error': error}), 400
        cursor.execute('''INSERT INTO applications (user_id, company, role, status, applied_on, location, job_url, notes)
                          VALUES (%s, %s, %s, %s, %s, %s, %s, %s)''',
                       (session['user_id'], *payload.values()))
        db.commit()
        return jsonify({'message': 'Application added', 'id': cursor.lastrowid}), 201
    finally:
        cursor.close(); db.close()


@app.route('/api/applications/<int:application_id>', methods=['GET', 'PUT', 'DELETE'])
@protected_route
def application(application_id):
    db = get_db(); cursor = db.cursor(dictionary=True)
    try:
        if request.method == 'GET':
            cursor.execute("SELECT id, user_id, company, role, status, DATE_FORMAT(applied_on, '%Y-%m-%d') AS applied_on, location, job_url, notes, updated_at FROM applications WHERE id = %s AND user_id = %s", (application_id, session['user_id']))
            item = cursor.fetchone()
            return (jsonify({'application': item}), 200) if item else (jsonify({'error': 'Application not found'}), 404)
        if request.method == 'DELETE':
            cursor.execute('DELETE FROM applications WHERE id = %s AND user_id = %s', (application_id, session['user_id']))
            db.commit()
            if not cursor.rowcount: return jsonify({'error': 'Application not found'}), 404
            return jsonify({'message': 'Application deleted'})
        payload, error = application_payload(request.get_json(silent=True) or {})
        if error: return jsonify({'error': error}), 400
        cursor.execute('''UPDATE applications SET company=%s, role=%s, status=%s, applied_on=%s, location=%s, job_url=%s, notes=%s
                          WHERE id=%s AND user_id=%s''', (*payload.values(), application_id, session['user_id']))
        db.commit()
        if not cursor.rowcount: return jsonify({'error': 'Application not found'}), 404
        return jsonify({'message': 'Application updated'})
    finally:
        cursor.close(); db.close()


@app.get('/api/applications/stats')
@protected_route
def application_stats():
    db = get_db(); cursor = db.cursor(dictionary=True)
    try:
        uid = session['user_id']
        cursor.execute('SELECT COUNT(*) AS total FROM applications WHERE user_id = %s', (uid,))
        total = cursor.fetchone()['total']
        cursor.execute('SELECT status, COUNT(*) AS count FROM applications WHERE user_id = %s GROUP BY status', (uid,))
        counts = {status: 0 for status in VALID_STATUSES}
        counts.update({row['status']: row['count'] for row in cursor.fetchall()})
        cursor.execute("SELECT id, user_id, company, role, status, DATE_FORMAT(applied_on, '%Y-%m-%d') AS applied_on, location, job_url, notes, updated_at FROM applications WHERE user_id = %s ORDER BY applied_on DESC, id DESC LIMIT 5", (uid,))
        return jsonify({'total': total, 'by_status': counts, 'latest': cursor.fetchall()})
    finally:
        cursor.close(); db.close()


if __name__ == '__main__':
    app.run(debug=True, port=5000)
