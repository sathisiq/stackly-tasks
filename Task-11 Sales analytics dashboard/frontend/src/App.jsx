import { useEffect, useState } from 'react'
import { getData } from './api'
import Navbar from './components/Navbar'
import FilterBar from './components/FilterBar'
import KPICards from './components/KPICards'
import RevenueLineChart from './components/RevenueLineChart'
import CategoryBarChart from './components/CategoryBarChart'
import CategoryPieChart from './components/CategoryPieChart'
import RegionBarChart from './components/RegionBarChart'
import TopProductsTable from './components/TopProductsTable'

const initialData = { kpis: null, monthly: [], categories: [], regions: [], products: [] }
export default function App() {
  const [filters, setFilters] = useState({ from: '', to: '', category: '' })
  const [categories, setCategories] = useState([])
  const [data, setData] = useState(initialData)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  useEffect(() => { getData('/categories').then(setCategories).catch(() => setError('Could not load categories.')) }, [])
  useEffect(() => {
    let active = true
    setLoading(true); setError('')
    Promise.all([getData('/kpis', filters), getData('/sales/monthly', filters), getData('/sales/by-category', filters), getData('/sales/by-region', filters), getData('/sales/top-products', filters)])
      .then(([kpis, monthly, categoryData, regions, products]) => { if (active) setData({ kpis, monthly: [...monthly].reverse(), categories: categoryData, regions, products }) })
      .catch((err) => { if (active) setError(err.response?.data?.error || 'Unable to reach Flask. Check that the backend is running.') })
      .finally(() => active && setLoading(false))
    return () => { active = false }
  }, [filters])
  return <><Navbar />
    <main className="dashboard">
      <section className="intro"><div><p className="eyebrow">Performance overview</p><h1>Sales analytics</h1><p>Track revenue, customer demand, and regional performance in one place.</p></div><span className="live-dot">Live data</span></section>
      <FilterBar filters={filters} setFilters={setFilters} categories={categories} />
      {error && <div className="error">{error}</div>}
      <KPICards data={data.kpis} loading={loading} />
      <section className="panel wide"><div className="panel-heading"><div><p className="eyebrow">Revenue trend</p><h2>Revenue over time</h2></div></div><RevenueLineChart data={data.monthly} loading={loading} /></section>
      <section className="two-col"><div className="panel"><div className="panel-heading"><div><p className="eyebrow">Sales mix</p><h2>Revenue by category</h2></div></div><CategoryBarChart data={data.categories} loading={loading} /></div><div className="panel"><div className="panel-heading"><div><p className="eyebrow">Category share</p><h2>Revenue distribution</h2></div></div><CategoryPieChart data={data.categories} loading={loading} /></div></section>
      <section className="two-col lower"><div className="panel"><div className="panel-heading"><div><p className="eyebrow">Market reach</p><h2>Revenue by region</h2></div></div><RegionBarChart data={data.regions} loading={loading} /></div><div className="panel"><div className="panel-heading"><div><p className="eyebrow">Leaderboard</p><h2>Top products</h2></div></div><TopProductsTable data={data.products} loading={loading} /></div></section>
    </main></>
}
