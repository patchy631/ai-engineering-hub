import os
from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    Column,
    String,
    Integer,
    insert,
)


def setup_sql_database():
    """Create a SQLite database with city statistics."""
    # Define the database file path
    db_path = "city_database.sqlite"

    # Check if database already exists
    db_exists = os.path.exists(db_path)

    # Create SQLite database engine
    engine = create_engine(f"sqlite:///{db_path}", future=True)
    metadata_obj = MetaData()

    # Create city_stats table
    table_name = "city_stats"
    city_stats_table = Table(
        table_name,
        metadata_obj,
        Column("city_name", String(16), primary_key=True),
        Column("population", Integer),
        Column("state", String(16), nullable=False),
    )

    # Only create tables if the database doesn't exist
    if not db_exists:
        metadata_obj.create_all(engine)

        # Insert sample data
        rows = [
            {"city_name": "New York City", "population": 8336000, "state": "New York"},
            {"city_name": "Los Angeles", "population": 3822000, "state": "California"},
            {"city_name": "Chicago", "population": 2665000, "state": "Illinois"},
            {"city_name": "Houston", "population": 2303000, "state": "Texas"},
            {"city_name": "Miami", "population": 449514, "state": "Florida"},
            {"city_name": "Seattle", "population": 749256, "state": "Washington"},
        ]

        # Insert each row into the table
        for row in rows:
            stmt = insert(city_stats_table).values(**row)
            with engine.begin() as connection:
                connection.execute(stmt)

        print(f"Created SQLite database at {db_path} with {len(rows)} city records")
    else:
        print(f"Using existing SQLite database at {db_path}")


# Execute the function directly if this script is run
if __name__ == "__main__":
    setup_sql_database()
