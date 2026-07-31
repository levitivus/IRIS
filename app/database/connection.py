"""
app/database/connection.py

Dedicated database connection module for PostgreSQL.
Provides a function to establish and return a database connection.
"""

from typing import Optional
import psycopg
from psycopg import OperationalError

import config


def get_db_connection() -> Optional[psycopg.Connection]:
    """
    Establishes and returns a connection to the PostgreSQL database.
    Reads database configuration parameters from the config module.

    Returns:
        psycopg.Connection: A valid PostgreSQL connection object if successful, None otherwise.
    """
    try:
        connection = psycopg.connect(
            host=config.DB_HOST,
            port=config.DB_PORT,
            dbname=config.DB_NAME,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
        )
        return connection
    except OperationalError as error:
        print(f"Error: Failed to connect to PostgreSQL database: {error}")
        return None
