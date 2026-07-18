import sqlite3
import pandas as pd
import time
from sqlalchemy import create_engine, MetaData, Table, Column, inspect, String, Integer, Float
from sqlalchemy.pool import StaticPool

def cleanup_resources(sqlite_connection, db_engine):
    """
    Clean up database-related resources. 
    Call this function on exit or when closing the application.
    """
    try:
        if sqlite_connection:
            sqlite_connection.close()
            print("SQLite connection closed.")
    except Exception as e:
        print(f"Error closing SQLite connection: {e}")
    
    try:
        if db_engine:
            db_engine.dispose()
            print("SQLAlchemy engine disposed.")
    except Exception as e:
        print(f"Error disposing SQLAlchemy engine: {e}")

def infer_column_types(df):
    """
    Infer column types from a DataFrame for dynamic table creation.
    """
    column_types = {}
    for col in df.columns:
        # First check if all values are numeric
        if pd.to_numeric(df[col], errors='coerce').notna().all():
            # Check if all values are integers
            if df[col].apply(lambda x: float(x).is_integer()).all():
                column_types[col] = Integer
            else:
                column_types[col] = Float
        else:
            column_types[col] = String(255)  # Default to string
    return column_types

def create_table_from_csv(engine, csv_file, table_name=None):
    """
    Create a new table in the database from a CSV file.
    Returns (table_name, DataFrame, error_message).
    """
    try:
        df = pd.read_csv(csv_file)
    except Exception as e:
        return None, None, f"Error reading CSV file: {str(e)}"
    
    # Clean the column names
    df.columns = [col.strip().replace(' ', '_').lower() for col in df.columns]
    
    if table_name is None:
        table_name = f"table_{int(time.time())}"

    metadata_obj = MetaData()
    inspector = inspect(engine)
    
    # If the table name already exists, generate a new one
    if table_name in inspector.get_table_names():
        i = 1
        while f"{table_name}_{i}" in inspector.get_table_names():
            i += 1
        table_name = f"{table_name}_{i}"
    
    # Infer column types
    column_types = infer_column_types(df)
    table = Table(table_name, metadata_obj,
                  *[Column(col, column_types[col]) for col in df.columns])

    try:
        metadata_obj.create_all(engine)
    except Exception as e:
        return None, None, f"Error creating table: {str(e)}"
    
    try:
        with engine.begin() as conn:
            data = df.to_dict(orient='records')
            for record in data:
                conn.execute(table.insert().values(**record))
    except Exception as e:
        return None, None, f"Error inserting data: {str(e)}"
    
    return table_name, df, None

def is_sql_result_satisfactory(result):
    """
    Check if an SQL response is likely satisfactory by scanning its text 
    for known 'no data' or error patterns.
    """
    result_text = str(result) if result is not None else ""
    if not result_text.strip():
        return False
    
    no_data_patterns = [
        "no data found",
        "no results",
        "could not find",
        "empty result",
        "no rows found",
        "i don't know",
        "i'm not sure",
        "none"
    ]
    for pattern in no_data_patterns:
        if pattern in result_text.lower():
            return False
    
    error_patterns = [
        "error",
        "exception",
        "invalid",
        "syntax error",
        "failed to execute"
    ]
    for pattern in error_patterns:
        if pattern in result_text.lower():
            return False
    
    if len(result_text.strip()) < 10:
        return False
    
    import re
    contains_numbers = bool(re.search(r'\d', result_text))
    contains_table_structure = ("|" in result_text or ":" in result_text)
    if not contains_numbers and not contains_table_structure:
        return False
    return True