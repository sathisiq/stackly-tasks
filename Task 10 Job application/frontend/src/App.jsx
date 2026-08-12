import { Navigate, Route, Routes } from 'react-router-dom'
import { createContext, useEffect, useState } from 'react'
import api from './api'
import ProtectedRoute from './components/ProtectedRoute'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import Dashboard from './pages/Dashboard'
import ApplicationsPage from './pages/ApplicationsPage'
import ApplicationFormPage from './pages/ApplicationFormPage'

export const AuthContext = createContext(null)

export default function App() {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  useEffect(() => { api.get('/api/me').then(r => setUser(r.data.user)).catch(() => setUser(null)).finally(() => setLoading(false)) }, [])
  if (loading) return <div className="page-center">Checking your session…</div>
  return <AuthContext.Provider value={{ user, setUser }}><Routes>
    <Route path="/login" element={user ? <Navigate to="/dashboard" /> : <LoginPage />} />
    <Route path="/register" element={user ? <Navigate to="/dashboard" /> : <RegisterPage />} />
    <Route element={<ProtectedRoute />}>
      <Route path="/dashboard" element={<Dashboard />} />
      <Route path="/applications" element={<ApplicationsPage />} />
      <Route path="/add" element={<ApplicationFormPage />} />
      <Route path="/applications/:id/edit" element={<ApplicationFormPage />} />
    </Route>
    <Route path="*" element={<Navigate to={user ? '/dashboard' : '/login'} />} />
  </Routes></AuthContext.Provider>
}
