"""Create the sales_analytics schema and deterministic sample data."""
import calendar
import os
import random
from datetime import date

import mysql.connector
from dotenv import load_dotenv

load_dotenv()
random.seed(11)
DB = dict(host=os.getenv("DB_HOST", "localhost"), port=int(os.getenv("DB_PORT", "3306")),
          user=os.getenv("DB_USER", "root"), password=os.getenv("DB_PASSWORD", "Sathis@2002"))
CATEGORIES = {
    "Electronics": [("Wireless Headphones", 89.99), ("Smart Watch", 149.99), ("Bluetooth Speaker", 64.99)],
    "Clothing": [("Classic Denim Jacket", 74.99), ("Cotton T-Shirt", 24.99), ("Running Shoes", 94.99)],
    "Food": [("Organic Coffee Beans", 18.50), ("Artisan Chocolate Box", 22.00), ("Protein Snack Pack", 16.75)],
    "Books": [("The Design Handbook", 34.99), ("Data Stories", 29.99), ("Creative Thinking", 19.99)],
    "Sports": [("Yoga Mat", 39.99), ("Stainless Water Bottle", 21.99), ("Resistance Bands", 27.50)],
}


def main():
    connection = mysql.connector.connect(**DB)
    cursor = connection.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS sales_analytics")
    cursor.execute("USE sales_analytics")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    for table in ("sales", "products", "categories"):
        cursor.execute(f"DROP TABLE IF EXISTS {table}")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    cursor.execute("CREATE TABLE categories (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(50) NOT NULL)")
    cursor.execute("""CREATE TABLE products (
        id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(100) NOT NULL, category_id INT NOT NULL,
        price DECIMAL(10,2) NOT NULL, FOREIGN KEY (category_id) REFERENCES categories(id))""")
    cursor.execute("""CREATE TABLE sales (
        id INT AUTO_INCREMENT PRIMARY KEY, product_id INT NOT NULL, quantity INT NOT NULL,
        total_amount DECIMAL(10,2) NOT NULL, sold_on DATE NOT NULL, region VARCHAR(50) NOT NULL,
        FOREIGN KEY (product_id) REFERENCES products(id))""")
    products = []
    for category, items in CATEGORIES.items():
        cursor.execute("INSERT INTO categories (name) VALUES (%s)", (category,))
        category_id = cursor.lastrowid
        for name, price in items:
            cursor.execute("INSERT INTO products (name, category_id, price) VALUES (%s, %s, %s)", (name, category_id, price))
            products.append((cursor.lastrowid, price))
    today = date.today()
    sales = []
    for month_offset in range(12):
        absolute_month = today.year * 12 + (today.month - 1) - month_offset
        year, zero_based_month = divmod(absolute_month, 12)
        month = zero_based_month + 1
        days = calendar.monthrange(year, month)[1]
        for _ in range(12):
            product_id, price = random.choice(products)
            quantity = random.randint(1, 6)
            sales.append((product_id, quantity, round(price * quantity, 2), date(year, month, random.randint(1, days)), random.choice(["North", "South", "East", "West"])))
    cursor.executemany("INSERT INTO sales (product_id, quantity, total_amount, sold_on, region) VALUES (%s,%s,%s,%s,%s)", sales)
    connection.commit()
    cursor.close(); connection.close()
    print(f"Seeded {len(CATEGORIES)} categories, {len(products)} products, and {len(sales)} sales records.")


if __name__ == "__main__":
    main()
