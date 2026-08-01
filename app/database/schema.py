"""
app/database/schema.py

Module responsible for creating and migrating PostgreSQL database tables (subjects, resources, and admins)
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
    sub_subcategory VARCHAR(80),
    subject_id INTEGER REFERENCES subjects(id) ON DELETE SET NULL,
    semester INTEGER,
    year INTEGER,
    module INTEGER,
    internal_exam INTEGER,
    title VARCHAR(255) NOT NULL,
    file_name VARCHAR(255),
    telegram_file_id TEXT,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

CREATE_ADMINS_TABLE = """
CREATE TABLE IF NOT EXISTS admins (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    role VARCHAR(30) NOT NULL DEFAULT 'admin',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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

ADD_SUB_SUBCATEGORY_COLUMN_RESOURCES = """
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'resources' AND column_name = 'sub_subcategory'
    ) THEN
        ALTER TABLE resources ADD COLUMN sub_subcategory VARCHAR(80);
    END IF;
END $$;
"""

MIGRATE_RESOURCES_CONSTRAINTS = """
DO $$
BEGIN
    -- Ensure file_name and telegram_file_id are nullable
    ALTER TABLE resources ALTER COLUMN file_name DROP NOT NULL;
    ALTER TABLE resources ALTER COLUMN telegram_file_id DROP NOT NULL;

    -- Add unique constraint for resources duplicate protection
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'resources_unique_key'
    ) THEN
        ALTER TABLE resources ADD CONSTRAINT resources_unique_key UNIQUE NULLS NOT DISTINCT (
            category, subcategory, sub_subcategory, subject_id, semester, year, module, internal_exam, title
        );
    END IF;
END $$;
"""


def create_tables() -> None:
    """
    Creates the 'subjects', 'resources', and 'admins' tables in the PostgreSQL database if they do not exist,
    and applies schema migrations for existing tables.
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
            cursor.execute(ADD_SUB_SUBCATEGORY_COLUMN_RESOURCES)
            cursor.execute(MIGRATE_RESOURCES_CONSTRAINTS)
            cursor.execute(CREATE_ADMINS_TABLE)
        connection.commit()
        print("Database schema created successfully.")
    except Exception as error:
        print(f"Error creating database schema: {error}")
    finally:
        connection.close()
