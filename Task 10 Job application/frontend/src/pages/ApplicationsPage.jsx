import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import Navbar from '../components/Navbar'
import api from '../api'
const statuses = ['All', 'Applied', 'Shortlisted', 'Interview Scheduled', 'Offer Received', 'Rejected']
const badge = s => `badge ${s.toLowerCase().replaceAll(' ', '-')}`
export default function ApplicationsPage() {
  const [applications, setApplications] = useState([]); const [filter, setFilter] = useState('All'); const [error, setError] = useState('')
  const load = () => api.get('/api/applications').then(r => setApplications(r.data.applications)).catch(e => setError(e.response?.data?.error || 'Could not load applications'))
  useEffect(() => { load() }, [])
  const shown = useMemo(() => filter === 'All' ? applications : applications.filter(a => a.status === filter), [applications, filter])
  async function remove(id) { if (!window.confirm('Delete this application?')) return; try { await api.delete(`/api/applications/${id}`); setApplications(a => a.filter(x => x.id !== id)) } catch (e) { setError(e.response?.data?.error || 'Could not delete application') } }
  return <><Navbar /><main className="container"><header className="page-heading"><div><h1>Applications</h1><p>{applications.length} application{applications.length === 1 ? '' : 's'} in your tracker.</p></div><Link className="button" to="/add">+ Add application</Link></header>{error && <div className="error">{error}</div>}<label className="filter">Filter by status <select value={filter} onChange={e => setFilter(e.target.value)}>{statuses.map(s => <option key={s}>{s}</option>)}</select></label>{shown.length ? <div className="table-wrap"><table><thead><tr><th>Company</th><th>Role</th><th>Status</th><th>Applied on</th><th>Location</th><th>Actions</th></tr></thead><tbody>{shown.map(a => <tr key={a.id}><td><strong>{a.company}</strong></td><td>{a.role}</td><td><span className={badge(a.status)}>{a.status}</span></td><td>{a.applied_on}</td><td>{a.location || '—'}</td><td className="actions"><Link to={`/applications/${a.id}/edit`}>Edit</Link><button onClick={() => remove(a.id)}>Delete</button></td></tr>)}</tbody></table></div> : <div className="empty">No applications match this filter.</div>}</main></>
}
