import { Cell, Legend, Pie, PieChart, ResponsiveContainer, Tooltip } from 'recharts'
import { Empty, money } from './ChartCommon'
const colors = ['#5963e8','#75bda9','#f4b56b','#e8869f','#8d83d9']
export default function CategoryPieChart({ data, loading }) { if (!data.length) return <Empty loading={loading} />; return <div className="chart pie-chart"><ResponsiveContainer width="100%" height="100%"><PieChart><Pie data={data} dataKey="revenue" nameKey="category" innerRadius="52%" outerRadius="76%" paddingAngle={3}>{data.map((item, i) => <Cell fill={colors[i % colors.length]} key={item.category}/>)}</Pie><Tooltip formatter={(v) => money(v)}/><Legend iconType="circle" iconSize={8}/></PieChart></ResponsiveContainer></div> }
