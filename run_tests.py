import duckdb
import pandas as pd
import sqlalchemy
import time

PG_CONN_STR = 'postgresql://postgres:postgres@localhost/column_vs_row'
TABLE_NAME = 'sales'

# Connect to PostgreSQL
pg_engine = sqlalchemy.create_engine(PG_CONN_STR)
# Connect to DuckDB (in memory store)
duckdb_con = duckdb.connect(database=':memory:', read_only=False)

# Step 1: Load data
print("Loading data into databases...")
df = pd.read_csv('sales_data.csv')

# Load into PostgreSQL (row-oriented database)
start = time.time()
df.to_sql(TABLE_NAME, pg_engine, if_exists='replace', index=False, chunksize=10000)
print(f"PostgreSQL load time: {time.time() - start:.2f}s")

# Load into DuckDB
start = time.time()
duckdb_con.execute("CREATE TABLE sales AS SELECT * FROM df")
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

# Compare with primary key applied
with pg_engine.connect() as con:
    con.execute(sqlalchemy.text(f'ALTER TABLE {TABLE_NAME} ADD PRIMARY KEY (transaction_id);'))
    con.commit()


start = time.time()
with pg_engine.connect() as con:
    res_pg_indexed = con.execute(sqlalchemy.text(f"SELECT * FROM {TABLE_NAME} WHERE transaction_id = '{transaction_id_to_find}'")).fetchone()

pg_indexed_time = time.time() - start
print(f"PostgreSQL time (with Primary Key Index): {pg_indexed_time:.6f}s")

# DuckDB query
start = time.time()
res_duck = duckdb_con.execute(f"SELECT * FROM {TABLE_NAME} WHERE transaction_id = ?", [transaction_id_to_find]).fetchone()
duckdb_time = time.time() - start
print(f"DuckDB time: {duckdb_time:.6f}s")
print(f"Winner: {'PostgreSQL (with index)' if pg_indexed_time < duckdb_time else 'DuckDB'}")
print("-" * 20)

# Test 2: Wide Aggregation (OLAP)
print("\n--- Test 2: Aggregating across millions of rows (OLAP workload) ---")
query = "SELECT store_id, SUM(quantity * unit_price * (1 - discount)) AS total_revenue FROM sales GROUP BY store_id"

# PostgreSQL Query 
start = time.time()
pd.read_sql(query, pg_engine)
pg_time = time.time() - start
print(f"PostgreSQL time: {pg_time:.2f}s")

# DuckDB query 
start = time.time()
duckdb_con.execute(query).fetchdf()
duckdb_time = time.time() - start
print(f"DuckDB time: {duckdb_time:.2f}s")
print(f"Winner: {'PostgreSQL' if pg_time < duckdb_time else 'DuckDB'}")
print("-" * 20)

