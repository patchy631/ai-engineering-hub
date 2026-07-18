import sqlite3
import os

def init_db():
    # Get the directory of this script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(current_dir, 'cities.db')
    schema_path = os.path.join(current_dir, 'schema.sql')

    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Read and execute the schema
    with open(schema_path, 'r') as f:
        schema = f.read()
        cursor.executescript(schema)

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db() 