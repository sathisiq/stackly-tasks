import { Link, useNavigate } from 'react-router-dom'
import { useContext } from 'react'
import api from '../api'
import { AuthContext } from '../App'

export default function Navbar() {
  const { user, setUser } = useContext(AuthContext); const navigate = useNavigate()
  async function logout() { await api.get('/api/logout'); setUser(null); navigate('/login') }
  return <nav><Link className="brand" to="/dashboard">JobTrack</Link><div className="nav-links"><Link to="/dashboard">Dashboard</Link><Link to="/applications">Applications</Link>
  {/* <Link className="add-link" to="/add">+ Add New</Link> */}
  {/* <span>Hi, {user?.username}</span> */}
  <button className="link-button" onClick={logout}>Logout</button></div></nav>
}
