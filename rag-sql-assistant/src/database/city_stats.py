"""
City Statistics Database Module

This module provides functionality to create and manage a SQLite database
with statistics about US cities, including their population and state.
"""
from typing import List, Dict, Any, Optional, Tuple

from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    Column,
    String,
    Integer,
    insert,
    select
)
from sqlalchemy.engine import Engine
from llama_index.core import SQLDatabase

class CityStatsDB:
    """Class to manage the city statistics database."""
    
    def __init__(self, db_path: str = None):
        """
        Initialize the city statistics database.
        
        Args:
            db_path: Path to the SQLite database file.
                     If None, creates an in-memory database.
        """
        if db_path:
            self.engine = create_engine(f"sqlite:///{db_path}", future=True)
        else:
            self.engine = create_engine("sqlite:///:memory:", future=True)
        
        self.metadata = MetaData()
        self.city_stats_table = self._create_table()
        self.metadata.create_all(self.engine)
    
    def _create_table(self) -> Table:
        """
        Create the city_stats table schema.
        
        Returns:
            Table: The SQLAlchemy Table object
        """
        return Table(
            "city_stats",
            self.metadata,
            Column("city_name", String(16), primary_key=True),
            Column("population", Integer),
            Column("state", String(16), nullable=False),
        )
    
    def populate_default_data(self) -> None:
        """Populate the database with default city statistics."""
        default_data = [
            {"city_name": "New York City", "population": 8336000, "state": "New York"},
            {"city_name": "Los Angeles", "population": 3822000, "state": "California"},
            {"city_name": "Chicago", "population": 2665000, "state": "Illinois"},
            {"city_name": "Houston", "population": 2303000, "state": "Texas"},
            {"city_name": "Miami", "population": 449514, "state": "Florida"},
            {"city_name": "Seattle", "population": 749256, "state": "Washington"},
        ]
        self.insert_data(default_data)
    
    def insert_data(self, cities_data: List[Dict[str, Any]]) -> None:
        """
        Insert data into the city_stats table.
        
        Args:
            cities_data: List of dictionaries with city information.
                        Each dictionary should contain 'city_name', 'population', and 'state'.
        """
        for city_data in cities_data:
            stmt = insert(self.city_stats_table).values(**city_data)
            with self.engine.begin() as connection:
                connection.execute(stmt)
    
    def get_all_cities(self) -> List[Tuple[str, int, str]]:
        """
        Retrieve all cities and their information from the database.
        
        Returns:
            List of tuples with (city_name, population, state)
        """
        with self.engine.connect() as connection:
            cursor = connection.exec_driver_sql("SELECT * FROM city_stats")
            return cursor.fetchall()
    
    def get_llama_index_sql_database(self) -> SQLDatabase:
        """
        Get a LlamaIndex SQLDatabase object for this database.
        
        Returns:
            SQLDatabase: A LlamaIndex SQLDatabase wrapper for the database
        """
        return SQLDatabase(self.engine, include_tables=["city_stats"])
    
    def get_engine(self) -> Engine:
        """
        Get the SQLAlchemy engine.
        
        Returns:
            Engine: The SQLAlchemy engine
        """
        return self.engine
    
    def get_city_by_name(self, city_name: str) -> Optional[Tuple[str, int, str]]:
        """
        Retrieve information for a specific city.
        
        Args:
            city_name: Name of the city to look up
            
        Returns:
            Tuple of (city_name, population, state) or None if not found
        """
        stmt = select(self.city_stats_table).where(self.city_stats_table.c.city_name == city_name)
        with self.engine.connect() as connection:
            result = connection.execute(stmt)
            city = result.fetchone()
            return city if city else None
