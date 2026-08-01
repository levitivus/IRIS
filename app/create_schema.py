"""
app/create_schema.py

Runner script to execute PostgreSQL database schema creation for IRIS.
"""

from app.database.schema import create_tables

if __name__ == "__main__":
    create_tables()
