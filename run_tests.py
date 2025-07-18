import duckdb
import pandas as pd
import sqlalchemy
import time

PG_CONN_STR = 'postgresql://postgres:postgres@localhost/column_vs_row'
TABLE_NAME = 'sales'

# Connect to PostgreSQL
pg_engine = sqlalchemy.create_engine(PG_CONN_STR)
# Connect to DuckDB (in memory store)
duckdb_conn = duckdb.connect(database=':memory:', read_only=False)

# Step 1: Load data
print("Loading data into databases...")
df = pd.read_csv('sales_data.csv')

# Load into PostgreSQL (row-oriented database)
start = time.time()
df.to_sql(TABLE_NAME, pg_engine, if_exists='replace', index=False, chuncksize=10000)
print(f"PostgreSQL load time: {time.time() - start:.2f}s")

# Load into DuckDB
start = time.time()
duckdb_conn.execute("CREATE TABLE sales AS SELECT * FROM df")
print(f"DuckDB load time: {time.time() - start:.2f}s")
print("-" * 20)

# Test 1: Point lookup (Get all columns related to a single transaction)
print("\n--- Test 1: Fetching a single full record (OLTP workload) ---")
# Get a transaction_id in the middle of the table to query
transaction_id_to_find = df['transaction_id'].iloc[len(df) // 2]

# PostgreSQL query
start = time.time()
with pg_engine.connect() as con:
    res_pg = con.execute(sqlalchemy.text(f"SELECT * FROM {TABLE_NAME} WHERE transaction_id = '{transaction_id_to_find}'")).fetchone()
print(f"PostgreSQL time: {time.time() - start:.6f}s")