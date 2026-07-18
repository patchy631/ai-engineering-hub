from sqlalchemy import insert, create_engine, MetaData, Table, Column, String, Integer
from llama_index.core import SQLDatabase
from llama_index.core.query_engine import NLSQLTableQueryEngine
from llama_index.core.tools import QueryEngineTool


class SQLQueryEngine:
    """
    A class to manage the SQL engine, create tables, and retrieve the SQL query tool.
    """

    def __init__(self, db_url="sqlite:///:memory:"):
        """
        Initializes the SQLQueryEngine with an in-memory SQLite database.

        Args:
            db_url (str): Database connection URL (default: SQLite in-memory).
        """
        self.engine = create_engine(db_url, future=True)
        self.metadata = MetaData()
        self._create_tables()

    def _create_tables(self):
        """Creates the city_stats table and inserts initial data."""
        city_stats_table = Table(
            "city_stats",
            self.metadata,
            Column("city_name", String(16), primary_key=True),
            Column("population", Integer),
            Column("state", String(16), nullable=False),
        )

        self.metadata.create_all(self.engine)

        # Insert initial city data
        rows = [
            {"city_name": "New York City", "population": 8336000, "state": "New York"},
            {"city_name": "Los Angeles", "population": 3822000, "state": "California"},
            {"city_name": "Chicago", "population": 2665000, "state": "Illinois"},
            {"city_name": "Houston", "population": 2303000, "state": "Texas"},
            {"city_name": "Miami", "population": 449514, "state": "Florida"},
            {"city_name": "Seattle", "population": 749256, "state": "Washington"},
        ]

        with self.engine.begin() as connection:
            for row in rows:
                stmt = insert(city_stats_table).values(**row)
                connection.execute(stmt)

    def get_sql_tool(self):
        """
        Creates and returns the SQL query tool for natural language queries.

        Returns:
            QueryEngineTool: A tool that enables natural language to SQL query translation.
        """
        sql_database = SQLDatabase(self.engine, include_tables=["city_stats"])
        sql_query_engine = NLSQLTableQueryEngine(
            sql_database=sql_database, tables=["city_stats"]
        )

        return QueryEngineTool.from_defaults(
            query_engine=sql_query_engine,
            description=(
                "Useful for translating a natural language query into a SQL query over"
                " a table containing: city_stats, with information on the population"
                " and state of various cities in the USA."
            ),
            name="sql_tool",
        )