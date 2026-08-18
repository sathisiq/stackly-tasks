export const money = (value) => `$${Number(value || 0).toLocaleString('en-US', { maximumFractionDigits: 0 })}`
export function Empty({ loading }) { return <div className="chart-empty">{loading ? 'Loading chart…' : 'No sales match these filters.'}</div> }
