import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, MetaData, Table, Column, String, Integer, insert, inspect
from llama_index.core import SQLDatabase, Settings
from llama_index.llms.openai import OpenAI
from llama_index.core.query_engine import NLSQLTableQueryEngine

class SQLSetup:
    def __init__(self, db_url="sqlite:///city_stats.db"):
        load_dotenv()
        os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')
        Settings.llm = OpenAI(model="gpt-3.5-turbo")
        
        self.db_url = db_url
        self.engine = create_engine(self.db_url, future=True)
        self.metadata = MetaData()
        self.table_name = "city_stats"
        
        self.city_stats_table = Table(
            self.table_name, self.metadata,
            Column("city_name", String(16), primary_key=True),
            Column("population", Integer),
            Column("state", String(16), nullable=False),
        )
        
        self._initialize_database()
        self.sql_database = SQLDatabase(self.engine, include_tables=[self.table_name])
        self.sql_query_engine = NLSQLTableQueryEngine(
            sql_database=self.sql_database, tables=[self.table_name]
        )

    def _initialize_database(self):
        inspector = inspect(self.engine)
        if not inspector.has_table(self.table_name):
            self.metadata.create_all(self.engine)
            self._insert_initial_data()
            print("Database and table created with initial data.")
        else:
            print("Database and table already exist. Skipping creation.")
    
    def _insert_initial_data(self):
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
                stmt = insert(self.city_stats_table).values(**row)
                connection.execute(stmt)

    def get_sql_query_engine(self):
        return self.sql_query_engine

# Usage
if __name__ == "__main__":
    sql_setup = SQLSetup()
    query_engine = sql_setup.get_sql_query_engine()
