import { useEffect, useState } from 'react'
import Navbar from '../components/Navbar'
import ApplicationCard from '../components/ApplicationCard'
import api from '../api'

const statuses = ['Applied', 'Shortlisted', 'Interview Scheduled', 'Offer Received', 'Rejected']
export default function Dashboard() {
  const [stats, setStats] = useState(null); const [error, setError] = useState('')
  useEffect(() => { api.get('/api/applications/stats').then(r => setStats(r.data)).catch(e => setError(e.response?.data?.error || 'Could not load dashboard')) }, [])
  return <><Navbar /><main className="container"><header className="page-heading"><div><h1>Your dashboard</h1><p>Keep your job search organized and moving forward.</p></div></header>{error && <div className="error">{error}</div>}{!stats ? <p>Loading dashboard…</p> : <><section className="stats"><div className="stat total"><span>Total applications</span><b>{stats.total}</b></div>{statuses.map(s => <div className="stat" key={s}><span>{s}</span><b>{stats.by_status[s]}</b></div>)}</section><section><h2>Latest applications</h2>{stats.latest.length ? <div className="latest-list">{stats.latest.map(a => <ApplicationCard key={a.id} application={a} />)}</div> : <div className="empty">No applications yet. Add your first one to get started.</div>}</section></>}</main></>
}
