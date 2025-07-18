import pandas as pd
from faker import Faker # For generating test data
import random
import time

fake = Faker()
num_records = 5_000_000 # Number convention for easier interpretation

print(f"Generating {num_records} records...")
start_time = time.time()

data = {
    'transaction_id': [fake.uuid4() for _ in range(num_records)],
    'product_id': [random.randint(1, 1000) for _ in range(num_records)],
    'customer_id': [random.randint(1,10000) for _ in range(num_records)],
    'store_id': [random.randint(1, 100) for _ in range(num_records)],
    'transaction_date': [fake.data_time_this_decade() for _ in range(num_records)],
    'quantity': [random.randint(1,5) for _ in range(num_records)],
    'unit_price': [round(random.uniform(5.0, 500.0), 2) for _ in range(num_records)],
    'discount': [round(random.uniform(0.0, 0.25), 2) for _ in range(num_records)]
}

df = pd.DataFrame(data)
df.to_csv('sales_data.csv', index=False)

end_time = time.time()
print(f"Data generation complete. Saved to sales_data.csv")
print(f"Time taken: {end_time - start_time:.2f} seconds")