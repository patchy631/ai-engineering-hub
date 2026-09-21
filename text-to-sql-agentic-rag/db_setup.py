from sqlalchemy import ( create_engine, MetaData, Table, Column, String, Integer, text)
from sqlalchemy import insert

SQL_TABLE_NAME = "city_stats"

def setup_db():
    # Use a file-based SQLite database
    engine = create_engine("sqlite:///city_stats.db", future=True)
    metadata_obj = MetaData()

    # Check if the table exists
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT name FROM sqlite_master WHERE type='table' AND name='city_stats';"))
        if result.fetchone():
            print("Table 'city_stats' already exists.")
            return engine

    # create city_stats SQL table
    city_stats_table = Table(
        SQL_TABLE_NAME,
        metadata_obj,
        Column("city", String(16), primary_key=True),
        Column("population", Integer),
        Column("state", String(16), nullable=False),
    )
    metadata_obj.create_all(engine)

    rows = [
        {"city": "New York City", "population": 8336000, "state": "New York"},
        {"city": "Los Angeles", "population": 3822000, "state": "California"},
        {"city": "Chicago", "population": 2665000, "state": "Illinois"},
        {"city": "Houston", "population": 2303000, "state": "Texas"},
        {"city": "Miami", "population": 449514, "state": "Florida"},
        {"city": "Seattle", "population": 749256, "state": "Washington"},
    ]

    for row in rows:
        stmt = insert(city_stats_table).values(**row)
        with engine.begin() as connection:
            connection.execute(stmt)
    return engine