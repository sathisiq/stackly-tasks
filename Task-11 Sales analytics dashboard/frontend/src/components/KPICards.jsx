const currency = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 })
export default function KPICards({ data, loading }) {
  const cards = data ? [{ label: 'Total revenue', value: currency.format(data.total_revenue), icon: '↗' }, { label: 'Total orders', value: data.total_orders.toLocaleString(), icon: '◫' }, { label: 'Average order value', value: currency.format(data.average_order_value), icon: '◈' }, { label: 'Best selling product', value: data.best_selling_product.name, detail: `${data.best_selling_product.units_sold} units sold`, icon: '★' }] : []
  return <section className="kpis">{loading && !data ? [1, 2, 3, 4].map((x) => <div className="kpi skeleton" key={x} />) : cards.map((card) => <article className="kpi" key={card.label}><div className="kpi-icon">{card.icon}</div><p>{card.label}</p><h2>{card.value}</h2>{card.detail && <small>{card.detail}</small>}</article>)}</section>
}
