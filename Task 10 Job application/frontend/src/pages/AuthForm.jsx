import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import api from '../api'

export default function AuthForm({ register = false, onLogin }) {
  const [form, setForm] = useState({ username: '', email: '', password: '', confirmPassword: '' }); const [error, setError] = useState(''); const navigate = useNavigate()
  const change = e => setForm({ ...form, [e.target.name]: e.target.value })
  async function submit(e) { e.preventDefault(); setError(''); if (register && form.password !== form.confirmPassword) return setError('Passwords do not match')
    try { const r = await api.post(register ? '/api/register' : '/api/login', form); if (register) navigate('/login'); else { onLogin(r.data.user); navigate('/dashboard') } } catch (e) { setError(e.response?.data?.error || 'Something went wrong. Please try again.') } }
  return <main className="auth-page"><form className="auth-form" onSubmit={submit}><h1>{register ? 'Create your account' : 'Welcome back'}</h1><p>{register ? 'Start tracking your next opportunity.' : 'Sign in to manage your applications.'}</p>{error && <div className="error">{error}</div>}<label>Username<input name="username" value={form.username} onChange={change} required /></label>{register && <label>Email<input name="email" type="email" value={form.email} onChange={change} required /></label>}<label>Password<input name="password" type="password" value={form.password} onChange={change} required /></label>{register && <label>Confirm password<input name="confirmPassword" type="password" value={form.confirmPassword} onChange={change} required /></label>}<button>{register ? 'Register' : 'Login'}</button><p className="switch">{register ? 'Already registered?' : 'New to JobTrack?'} <Link to={register ? '/login' : '/register'}>{register ? 'Login' : 'Create an account'}</Link></p></form></main>
}
