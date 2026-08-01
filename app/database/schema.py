"""
app/database/schema.py

Module responsible for creating PostgreSQL database tables (subjects and resources)
according to the IRIS Database Blueprint.
"""

from app.database.connection import get_db_connection


CREATE_SUBJECTS_TABLE = """
CREATE TABLE IF NOT EXISTS subjects (
    id SERIAL PRIMARY KEY,
    semester INTEGER NOT NULL,
    subject_code VARCHAR(25) UNIQUE NOT NULL,
    subject_name VARCHAR(255) NOT NULL
);
"""

CREATE_RESOURCES_TABLE = """
CREATE TABLE IF NOT EXISTS resources (
    id SERIAL PRIMARY KEY,
    category VARCHAR(50) NOT NULL,
    subcategory VARCHAR(80),
    subject_id INTEGER REFERENCES subjects(id) ON DELETE SET NULL,
    semester INTEGER,
    year INTEGER,
    module INTEGER,
    internal_exam INTEGER,
    title VARCHAR(255) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    telegram_file_id TEXT NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

ADD_UNIQUE_CONSTRAINT_SUBJECTS = """
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'subjects_subject_code_key'
    ) THEN
        ALTER TABLE subjects ADD CONSTRAINT subjects_subject_code_key UNIQUE (subject_code);
    END IF;
END $$;
"""


def create_tables() -> None:
    """
    Creates the 'subjects' and 'resources' tables in the PostgreSQL database if they do not exist.
    """
    connection = get_db_connection()
    if connection is None:
        print("Failed to establish database connection. Table creation aborted.")
        return

    try:
        with connection.cursor() as cursor:
            cursor.execute(CREATE_SUBJECTS_TABLE)
            cursor.execute(ADD_UNIQUE_CONSTRAINT_SUBJECTS)
            cursor.execute(CREATE_RESOURCES_TABLE)
        connection.commit()
        print("Database schema created successfully.")
    except Exception as error:
        print(f"Error creating database schema: {error}")
    finally:
        connection.close()
