# Job Application Tracker

A full-stack personal job application tracker built with React, Vite, Flask, and MySQL. Each account can only access its own application records.

## Features

- Session-based registration, login, logout, and protected React routes
- Create, list, filter, edit, and delete applications
- Dashboard showing total, status counts, and the latest five entries
- Axios client configured to send cookies with every request

## Setup

1. Create the database and tables by running `backend/schema.sql` in MySQL.
2. In `backend`, create a `.env` file based on `.env.example`, or set the same environment variables in your terminal. Install and run:

   ```bash
   cd backend
   python -m venv venv
   # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   python app.py
   ```

3. In another terminal, install and start the React app:

   ```bash
   cd frontend
   npm install
   npm run dev
   ```

Open the Vite address shown in the terminal (normally `http://localhost:5173`).

## Write-up

### What is React Router, and how is the route protected?

React Router maps browser paths to React pages without a full page refresh. The app checks `/api/me` once when it starts and holds the authenticated user in React context. `ProtectedRoute` renders nested routes only when that user exists; otherwise it redirects to `/login`.

```jsx
export default function ProtectedRoute() {
  const { user } = useContext(AuthContext)
  return user ? <Outlet /> : <Navigate to="/login" replace />
}
```

### Axios vs. fetch

`fetch` is built into browsers but needs manual JSON conversion and more explicit error handling. Axios automatically parses JSON, offers a concise API, and centralizes settings. This project uses one Axios instance in `src/api.js` with `withCredentials: true`, so browser session cookies accompany each API call.

### How does the app know a user is logged in?

The Flask session cookie is the source of truth and stays HTTP-only rather than being saved in browser storage. On startup, React calls `/api/me`; the returned user is saved only in in-memory React context and is consumed by the Navbar and protected routes.

### Connecting React and Flask

The key issue is cross-origin session cookies because Vite and Flask use separate ports. Flask-CORS is configured with the exact Vite origin and `supports_credentials=True`; Axios uses `withCredentials: true`. Together they allow the server session to travel safely with requests.
