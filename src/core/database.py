"""Database interface module for Excel Query Bot.

Classes:
    Database: Main database interface class for Excel data operations.
"""

from sqlalchemy import create_engine, inspect
from sqlmodel import JSON, Column, Field, Session, SQLModel, create_engine, text, Integer, select
from typing import Dict, NoReturn, Optional, List, Any

class Database:
    """SQLAlchemy-based database interface for Excel data operations.

    Attributes:
        db_url (str): SQLAlchemy database connection string.
        engine (sqlalchemy.Engine): SQLAlchemy engine for database operations.

    """
    def __init__(self, cfg):
        """Initialize database connection using configuration settings.

        Args:
            cfg (dynaconf.Dynaconf): Configuration object containing database settings.
                Expected structure:
                - RDBMS.NAME: Database type (e.g., 'postgresql')
                - RDBMS.USERNAME: Database username
                - RDBMS_PASSWORD.PASSWORD: Database password
                - RDBMS.HOST: Database host address
                - RDBMS.PORT: Database port number
                - RDBMS.DATABASE_NAME: Target database name

        """
        self.db_url = f"{cfg['RDBMS']['NAME']}://{cfg['RDBMS']['USERNAME']}:{cfg['RDBMS_PASSWORD']['PASSWORD']}@{cfg['RDBMS']['HOST']}:{cfg['RDBMS']['PORT']}/{cfg['RDBMS']['DATABASE_NAME']}"
        self.engine = create_engine(self.db_url)
        
    def save_df(self, df, table_name: str):
        """Save a pandas DataFrame to a database table with optimized performance.

        Args:
            df (pd.DataFrame): The DataFrame containing data to be saved.
            table_name (str): Target table name in the database.

        """        
        with self.engine.connect() as connection:
            df.to_sql(table_name, con=connection, if_exists='replace', index=False, chunksize=1000)
            
    def extract_schema(self, table_name):
        """Extract database table schema formatted for AI prompt construction.

        Args:
            table_name (str): Name of the table to inspect.

        Returns:
            str: Formatted JSON-like string containing table schema information.

        """
        inspector = inspect(self.engine)
        columns_info = inspector.get_columns(table_name)
        
        column_schema_lines = []
        for col in columns_info:
            column_schema_lines.append(
                f"""            {{
                    name: '{col['name']}',
                    type: '{str(col['type'])}'
                }}"""
            )
        
        column_schema_str = ",\n".join(column_schema_lines)
        
        schema = f"""
                {{
                    table: '{table_name}',
                    columns: [
            {column_schema_str}
                    ]
                }}"""
        
        return schema
            