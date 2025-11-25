import sqlite3
from sqlalchemy import create_engine, MetaData, Table, Column, String, Integer, insert

# Create a local SQLite database file
engine = create_engine("sqlite:///city_data.db", future=True)
metadata_obj = MetaData()

# Define the city_stats table
city_stats_table = Table(
    "city_stats",
    metadata_obj,
    Column("city_name", String(16), primary_key=True),
    Column("population", Integer),
    Column("state", String(16), nullable=False),
)

# Create the table
metadata_obj.create_all(engine)

# Insert city population data
rows = [
    {"city_name": "New York City", "population": 8336000, "state": "New York"},
    {"city_name": "Los Angeles", "population": 3822000, "state": "California"},
    {"city_name": "Chicago", "population": 2665000, "state": "Illinois"},
    {"city_name": "Houston", "population": 2303000, "state": "Texas"},
    {"city_name": "Miami", "population": 449514, "state": "Florida"},
    {"city_name": "Seattle", "population": 749256, "state": "Washington"},
]

# Insert data
with engine.begin() as connection:
    for row in rows:
        connection.execute(insert(city_stats_table).values(**row))

print("Database setup complete! Data stored in 'city_data.db'")
