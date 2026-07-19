"""
Load the cleaned, sentiment-scored dataset into a SQLite database
so it can be queried with SQL (03_queries.sql) and connected to Power BI.
"""
import sqlite3
import pandas as pd

IN_PATH = "data/amazon_with_sentiment.csv"
DB_PATH = "data/amazon.db"

df = pd.read_csv(IN_PATH)

conn = sqlite3.connect(DB_PATH)
df.to_sql("products", conn, if_exists="replace", index=False)

conn.execute("CREATE INDEX IF NOT EXISTS idx_main_category ON products(main_category)")
conn.execute("CREATE INDEX IF NOT EXISTS idx_rating ON products(rating)")
conn.commit()

cur = conn.execute("SELECT COUNT(*) FROM products")
print(f"Loaded {cur.fetchone()[0]} rows into {DB_PATH} (table: products)")
conn.close()
