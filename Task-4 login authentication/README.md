# User Login & Authentication System

A Flask, MySQL, and vanilla JavaScript authentication application. It provides registration, bcrypt password hashing, login/logout, server-side sessions, and protected dashboard/profile APIs.

## Setup

1. Create the database and table: `mysql -u root -p < schema.sql`.
2. Copy `.env.example` to `.env` and set the MySQL credentials and a strong `FLASK_SECRET_KEY`. Export these values in your shell (the app reads environment variables).
3. Create and activate a virtual environment, then install dependencies: `pip install -r requirements.txt`.
4. Run `python app.py`, then open `http://localhost:5000`.

The default page is the login screen. The full flow is Register → Login → Dashboard → Logout.

## API status codes

`POST /register` returns 201 on success, 400 for invalid input, and 409 for an existing username/email. `POST /login` returns 200 or 401. Protected `GET /dashboard` and `GET /profile` return 401 without a valid session. `GET /logout` clears the session and returns 200.

## Required write-up

*What is password hashing and why is plain text dangerous?*
 Hashing transforms a password into a one-way value. Bcrypt also salts it and is intentionally slow. If a database is exposed, plaintext passwords let an attacker immediately access accounts and often reuse those passwords elsewhere; a bcrypt hash must instead be cracked individually.

*What is a session and how does Flask use it?*
 A session associates requests from the same logged-in browser. This app stores `user_id`, username, and role in a server-side Flask-Session record; the browser receives only a signed session identifier cookie. Each protected route checks that session before it returns data.

*What happens when a wrong password is entered?*
 The backend reads the username's stored bcrypt hash and uses `check_password_hash` to compare it with the submitted password. A mismatch returns `401` with “Invalid username or password,” creates no session, and never exposes the hash or password.