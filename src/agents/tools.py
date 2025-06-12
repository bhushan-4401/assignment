"""LangChain tools for Excel Query Bot.

Classes:
    SqlQueryTool: LangChain tool for executing SQL SELECT queries on Excel data.
"""

from typing import Any
from langchain.tools.base import BaseTool
import pandas as pd
from pydantic import Field


class SqlQueryTool(BaseTool):
    """LangChain tool for executing SQL SELECT queries on Excel data.

    Attributes:
        name (str): Tool identifier used by LangChain agents ("sql_query").
        description (str): Brief description of tool functionality for agent reasoning.
        text_db (Any): Database interface object with SQLAlchemy engine attribute.

    """
    name: str = "sql_query"
    description: str = "Executes SQL SELECT queries on a relational database"
    text_db: Any = Field(None)

    def __init__(self, generator, text_db, **kwargs) -> None:
        """Initialize the SQL query tool with database connection.

        Args:
            generator: Language model instance (required for LangChain compatibility).
            text_db: Database interface object with SQLAlchemy engine attribute.
            **kwargs: Additional keyword arguments passed to BaseTool constructor.

        """
        super().__init__(generator=generator,text_db = text_db,**kwargs)

    def _run(self, query: str, **kwargs: Any):
        """Execute a SQL SELECT query and return structured results.

        Executes the provided SQL query against the database using pandas
        and SQLAlchemy, returning the results as a list of dictionaries
        for easy processing by downstream components.

        Args:
            query (str): SQL SELECT query string to execute.
            **kwargs (Any): Additional keyword arguments (currently unused).

        Returns:
            List[Dict[str, Any]]: Query results as a list of dictionaries.

        """
        return pd.read_sql_query(query, self.text_db.engine).to_dict(orient='records')