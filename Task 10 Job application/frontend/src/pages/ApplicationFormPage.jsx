import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import Navbar from '../components/Navbar'
import api from '../api'
const statuses = ['Applied', 'Shortlisted', 'Interview Scheduled', 'Offer Received', 'Rejected']
const initial = { company: '', role: '', status: 'Applied', applied_on: new Date().toISOString().slice(0, 10), location: '', job_url: '', notes: '' }
export default function ApplicationFormPage() {
  const { id } = useParams(); const editing = Boolean(id); const [form, setForm] = useState(initial); const [error, setError] = useState(''); const [loading, setLoading] = useState(editing); const navigate = useNavigate()
  useEffect(() => { if (editing) api.get(`/api/applications/${id}`).then(r => setForm({ ...r.data.application, applied_on: r.data.application.applied_on.slice(0, 10) })).catch(e => setError(e.response?.data?.error || 'Could not load application')).finally(() => setLoading(false)) }, [id, editing])
  const change = e => setForm({ ...form, [e.target.name]: e.target.value })
  async function submit(e) { e.preventDefault(); setError(''); try { if (editing) await api.put(`/api/applications/${id}`, form); else await api.post('/api/applications', form); navigate('/applications') } catch (e) { setError(e.response?.data?.error || 'Could not save application') } }
  return <><Navbar /><main className="container form-page"><h1>{editing ? 'Edit application' : 'Add application'}</h1>{loading ? <p>Loading application…</p> : <form className="application-form" onSubmit={submit}>{error && <div className="error">{error}</div>}<label>Company<input name="company" value={form.company} onChange={change} required /></label><label>Role<input name="role" value={form.role} onChange={change} required /></label><label>Status<select name="status" value={form.status} onChange={change}>{statuses.map(s => <option key={s}>{s}</option>)}</select></label><label>Applied on<input name="applied_on" type="date" value={form.applied_on} onChange={change} required /></label><label>Location<input name="location" value={form.location || ''} onChange={change} /></label><label>Job URL<input name="job_url" type="url" placeholder="https://…" value={form.job_url || ''} onChange={change} /></label><label className="wide">Notes<textarea name="notes" rows="5" value={form.notes || ''} onChange={change} /></label><div className="form-actions"><button>Save application</button><button type="button" className="secondary" onClick={() => navigate('/applications')}>Cancel</button></div></form>}</main></>
}
