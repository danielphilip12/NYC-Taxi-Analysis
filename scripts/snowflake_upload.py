import numpy as np
import pandas as pd
import pyarrow as pa
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas

import sys
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

user=os.getenv("user")
password=os.getenv("password")
account=os.getenv("account")
warehouse=os.getenv("warehouse")         
database=os.getenv('database')
schema=os.getenv('schema')

# Add the project root directory to sys.path
# (Adjust .parent counts depending on how deep your notebook is)
project_root = Path.cwd().parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

# Now import directly from your folder structure
from scripts.data_cleaning import clean_data, add_columns

month_name_num = {
    "Jan": "01",
    "Feb": "02",
    "Mar": "03",
    "Apr": "04",
    "May": "05",
    "Jun": "06",
    "Jul": "07",
    "Aug": "08",
    "Sep": "09",
    "Oct": "10",
    "Nov": "11",
    "Dec": "12",
}

monthly_data = {}

print("Loading and Cleaning Data")
for key, value in month_name_num.items():
    df = pd.read_parquet(f"https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-{value}.parquet")
    cleaned_df = clean_data(df, int(value))
    monthly_data[key] = cleaned_df
print("Data loaded and cleaned")

print("Connecting to Snowflake")
conn = snowflake.connector.connect(
    user=user,
    password=password,
    account=account,  
    warehouse=warehouse,             
    database=database,
    schema=schema
)
with conn.cursor() as cur:
    cur.execute(f"USE DATABASE {database}")
    cur.execute(f"USE SCHEMA {schema}")

print("Connected to Snowflake")
TABLE_MAPPING = [
    (0, 'FACT_TRIPS_ANALYTICAL'),
    (1, 'FACT_REFUND_CANDIDATES'),
    (2, 'FACT_NEGATIVE_TRIPS'),
    (3, 'FACT_ZERO_PASSENGER')
]
print("Uploading to Snowflake")
try:
    # Iterate through each table type (tuple index)
    for tuple_idx, table_name in TABLE_MAPPING:
        print(f"\n==========================================")
        print(f"Starting pipeline for table: {table_name}")
        print(f"==========================================")
        
        # Track whether we are uploading the very first month to establish table schema
        is_first_month = True
        
        # Loop through each month key in your dictionary (e.g., 'jan', 'feb', ...)
        for month_key, df_tuple in monthly_data.items():
            # Grab the specific DataFrame for this category/month
            df = df_tuple[tuple_idx].copy().reset_index(drop=True)
            
            # Skip if DataFrame is empty to avoid Snowflake type inference errors
            if df.empty:
                print(f"[{table_name}] Skipping {month_key.upper()} (0 rows).")
                continue
            
            # Standardize column names to uppercase (Snowflake default convention)
            df.columns = df.columns.str.upper()
            
            print(f"[{table_name}] Uploading {month_key.upper()} ({len(df):,} rows)...")
            
            # Upload month data to Snowflake
            success, nchunks, nrows, _ = write_pandas(
                conn=conn,
                df=df,
                table_name=table_name,
                database=database,
                schema=schema,
                auto_create_table=is_first_month,  # True ONLY for Month 1 (creates schema)
                overwrite=is_first_month           # True ONLY for Month 1 (replaces existing table if re-running)
            )
            
            print(f"  └─ Success! Appended {nrows:,} rows to {table_name}.")
            
            # After Month 1 creates/overwrites the table, set flag to append mode
            is_first_month = False

    print("\nAll data successfully loaded into Snowflake!")

finally:
    # Ensure connection closes properly even if an error occurs mid-script
    conn.close()
    print("Snowflake connection closed.")