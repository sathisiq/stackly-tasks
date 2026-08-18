import os
from datetime import date
from decimal import Decimal

import mysql.connector
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
CORS(app)


def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", "Sathis@2002"),
        database=os.getenv("DB_NAME", "sales_analytics"),
    )


def parse_filters():
    """Return safe filter SQL and parameters shared by every analytics query."""
    clauses, params = [], []
    from_date = request.args.get("from")
    to_date = request.args.get("to")
    category = request.args.get("category")

    for value, label in ((from_date, "from"), (to_date, "to")):
        if value:
            try:
                date.fromisoformat(value)
            except ValueError:
                return None, None, f"Invalid {label} date. Use YYYY-MM-DD."
    if from_date and to_date and from_date > to_date:
        return None, None, "'from' date must be before 'to' date."

    if from_date:
        clauses.append("s.sold_on >= %s")
        params.append(from_date)
    if to_date:
        clauses.append("s.sold_on <= %s")
        params.append(to_date)
    if category:
        clauses.append("c.name = %s")
        params.append(category)
    return (" WHERE " + " AND ".join(clauses)) if clauses else "", params, None


def fetch_all(query, params=()):
    connection = get_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, params)
        rows = cursor.fetchall()
        # mysql-connector returns DECIMAL columns as Decimal. Charts should receive JSON numbers.
        return [{key: float(value) if isinstance(value, Decimal) else value for key, value in row.items()} for row in rows]
    finally:
        cursor.close()
        connection.close()


def filtered_response(query):
    where, params, error = parse_filters()
    if error:
        return jsonify({"error": error}), 400
    return jsonify(fetch_all(query.format(where=where), params))


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/categories")
def categories():
    return jsonify(fetch_all("SELECT id, name FROM categories ORDER BY name"))


@app.get("/api/kpis")
def kpis():
    where, params, error = parse_filters()
    if error:
        return jsonify({"error": error}), 400
    summary = fetch_all("""
        SELECT COALESCE(SUM(s.total_amount), 0) AS total_revenue,
               COUNT(s.id) AS total_orders,
               COALESCE(AVG(s.total_amount), 0) AS average_order_value
        FROM sales s
        JOIN products p ON p.id = s.product_id
        JOIN categories c ON c.id = p.category_id
        {where}
    """.format(where=where), params)[0]
    best = fetch_all("""
        SELECT p.name, COALESCE(SUM(s.quantity), 0) AS units_sold
        FROM sales s
        JOIN products p ON p.id = s.product_id
        JOIN categories c ON c.id = p.category_id
        {where}
        GROUP BY p.id, p.name
        ORDER BY units_sold DESC, p.name ASC LIMIT 1
    """.format(where=where), params)
    return jsonify({
        "total_revenue": float(summary["total_revenue"]),
        "total_orders": summary["total_orders"],
        "average_order_value": float(summary["average_order_value"]),
        "best_selling_product": best[0] if best else {"name": "No sales", "units_sold": 0},
    })


@app.get("/api/sales/monthly")
def monthly_sales():
    return filtered_response("""
        SELECT DATE_FORMAT(s.sold_on, '%b %Y') AS month,
               DATE_FORMAT(s.sold_on, '%Y-%m') AS sort_month,
               SUM(s.total_amount) AS revenue
        FROM sales s JOIN products p ON p.id=s.product_id
        JOIN categories c ON c.id=p.category_id
        {where}
        GROUP BY YEAR(s.sold_on), MONTH(s.sold_on), month, sort_month
        ORDER BY sort_month DESC LIMIT 12
    """)


@app.get("/api/sales/by-category")
def sales_by_category():
    return filtered_response("""
        SELECT c.name AS category, SUM(s.total_amount) AS revenue
        FROM sales s JOIN products p ON p.id=s.product_id
        JOIN categories c ON c.id=p.category_id
        {where} GROUP BY c.id, c.name ORDER BY revenue DESC
    """)


@app.get("/api/sales/by-region")
def sales_by_region():
    return filtered_response("""
        SELECT s.region, SUM(s.total_amount) AS revenue
        FROM sales s JOIN products p ON p.id=s.product_id
        JOIN categories c ON c.id=p.category_id
        {where} GROUP BY s.region ORDER BY revenue DESC
    """)


@app.get("/api/sales/top-products")
def top_products():
    return filtered_response("""
        SELECT p.name AS product, c.name AS category, SUM(s.quantity) AS units_sold,
               SUM(s.total_amount) AS total_revenue
        FROM sales s JOIN products p ON p.id=s.product_id
        JOIN categories c ON c.id=p.category_id
        {where} GROUP BY p.id, p.name, c.name
        ORDER BY total_revenue DESC LIMIT 5
    """)


@app.get("/api/sales/filter")
def filtered_summary():
    return kpis()


@app.errorhandler(mysql.connector.Error)
def database_error(error):
    app.logger.exception("MySQL error")
    return jsonify({
        "error": "Database connection failed. Check backend/.env, ensure MySQL is running, then run python seed.py.",
        "detail": str(error),
    }), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
