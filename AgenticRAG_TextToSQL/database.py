from sqlalchemy import create_engine, MetaData, Table, Column, String, Integer, insert

# Initialize the SQLite database engine (sumit)
engine = create_engine("sqlite:///:memory:", future=True)
metadata_obj = MetaData()

# Define city statistics table
table_name = "city_stats"
city_stats_table = Table(
    table_name,
    metadata_obj,
    Column("city_name", String(16), primary_key=True),
    Column("population", Integer),
    Column("state", String(16), nullable=False),
)

# Create the table
metadata_obj.create_all(engine)

# Insert initial data
rows = [
    {"city_name": "New York City", "population": 8336000, "state": "New York"},
    {"city_name": "Los Angeles", "population": 3822000, "state": "California"},
    {"city_name": "Chicago", "population": 2665000, "state": "Illinois"},
    {"city_name": "Houston", "population": 2303000, "state": "Texas"},
    {"city_name": "Miami", "population": 449514, "state": "Florida"},
    {"city_name": "Seattle", "population": 749256, "state": "Washington"},
]
for row in rows:
    stmt = insert(city_stats_table).values(**row)
    with engine.begin() as connection:
        connection.execute(stmt)

def get_database_engine():
    """Returns the database engine instance."""
    return engine
