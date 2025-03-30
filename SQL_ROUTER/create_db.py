from sqlalchemy import create_engine, MetaData, Table, Column, String, Integer, insert


def create_sqlite_db(db_path="city_stats.db"):
    # Create engine pointing to a file
    engine = create_engine(f"sqlite:///{db_path}", future=True)
    metadata_obj = MetaData()

    # Define the city_stats table
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

    # Insert data
    rows = [
        {"city_name": "New York City", "population": 8336000, "state": "New York"},
        {"city_name": "Los Angeles", "population": 3822000, "state": "California"},
        {"city_name": "Chicago", "population": 2665000, "state": "Illinois"},
        {"city_name": "Houston", "population": 2303000, "state": "Texas"},
        {"city_name": "Miami", "population": 449514, "state": "Florida"},
        {"city_name": "Seattle", "population": 749256, "state": "Washington"},
    ]

    with engine.begin() as connection:
        for row in rows:
            stmt = insert(city_stats_table).values(**row)
            connection.execute(stmt)

    # Verify contents
    with engine.connect() as connection:
        result = connection.execute(city_stats_table.select()).fetchall()
        print("Database contents:", result)

    return engine, table_name


if __name__ == "__main__":
    create_sqlite_db()
