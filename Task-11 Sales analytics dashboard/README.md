# Sales Analytics Dashboard

A full-stack business intelligence dashboard built with React, Recharts, Flask, and MySQL. It visualises sales performance through KPI cards, revenue trend, category and region charts, plus a top-products leaderboard. All reports update together when a date or category filter changes.

## Features

- Four live KPI cards: total revenue, order count, average order value, and best selling product
- Monthly revenue area/line chart, category bar and pie charts, horizontal region chart
- Top-five products leaderboard
- Shared date-range and category filtering for every API route
- Responsive layout and loading states

## Setup

### 1. Create and seed the database

Install MySQL and create `backend/.env` from `backend/.env.example`, filling in your local password. Then:

```powershell
cd backend
py -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python seed.py
python app.py
```

`seed.py` creates the `sales_analytics` database, all three tables, five categories, fifteen products, and 144 varied sales records from the last twelve months. It deliberately resets these dashboard tables each time it runs.

### 2. Run the frontend

In another terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open the Vite URL (normally `http://localhost:5173`). Set `VITE_API_URL` if Flask is hosted somewhere other than `http://localhost:5000/api`.

## API endpoints

| Route | Purpose |
| --- | --- |
| `GET /api/kpis` | Four overview metrics |
| `GET /api/categories` | Category dropdown options |
| `GET /api/sales/monthly` | Revenue by month |
| `GET /api/sales/by-category` | Revenue by category |
| `GET /api/sales/by-region` | Revenue by region |
| `GET /api/sales/top-products` | Five products by revenue |
| `GET /api/sales/filter` | Filtered KPI summary |

The analytics routes accept `?from=YYYY-MM-DD&to=YYYY-MM-DD&category=Electronics`.

## Required write-up

### Monthly revenue query

```sql
SELECT DATE_FORMAT(s.sold_on, '%b %Y') AS month,
       SUM(s.total_amount) AS revenue
FROM sales s
GROUP BY YEAR(s.sold_on), MONTH(s.sold_on)
ORDER BY YEAR(s.sold_on), MONTH(s.sold_on);
```

`DATE_FORMAT` turns a date into a readable label such as `Aug 2026`. `GROUP BY` collects every sale occurring in the same calendar month, which allows `SUM` to calculate one revenue total per month. Grouping by numeric year and month ensures chronological order even when the displayed label is text.

### How filters re-fetch charts

`App.jsx` owns `from`, `to`, and `category` in a single `filters` state object. A `useEffect` whose dependency is `[filters]` runs whenever the FilterBar changes that state. It requests all five analytics endpoints with the same query parameters using `Promise.all`, then replaces every chart’s data together.

### Bar chart vs line chart

Use a bar chart to compare distinct categories, such as revenue by region or product category. Use a line chart for ordered, continuous sequences such as monthly revenue: its connected points make direction and trends over time easy to see.

### ResponsiveContainer

Recharts’ `ResponsiveContainer` measures the chart’s parent and sizes the chart to it. This makes charts adapt to desktop, tablet, and phone widths without fixed pixel widths, which is essential in a responsive dashboard.
