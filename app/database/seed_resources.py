"""
app/database/seed_resources.py

Module responsible for reading data/resources.csv, mapping subject codes to subject_ids,
and seeding the PostgreSQL 'resources' table safely without duplicates.
"""

import csv
import os
from typing import Dict, List, Optional, Tuple

from app.database.connection import get_db_connection


def clean_val(val: Optional[str]) -> Optional[str]:
    """Helper to convert empty strings or whitespace to None."""
    if val is None:
        return None
    val_str = val.strip()
    return val_str if val_str != "" else None


def clean_int(val: Optional[str]) -> Optional[int]:
    """Helper to convert numeric string values to integers or None."""
    cleaned = clean_val(val)
    if cleaned is not None:
        try:
            return int(cleaned)
        except ValueError:
            return None
    return None


def get_subject_mapping(cursor) -> Dict[str, int]:
    """Queries the subjects table and returns a dictionary mapping subject_code to subject_id."""
    cursor.execute("SELECT subject_code, id FROM subjects;")
    return {row[0]: row[1] for row in cursor.fetchall()}


def parse_resources_file(
    file_path: str, subject_map: Dict[str, int]
) -> List[Tuple]:
    """
    Reads data/resources.csv and converts rows into tuples suitable for insertion.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Resources CSV file not found: {file_path}")

    resources = []
    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            category = clean_val(row.get("Category"))
            subcategory = clean_val(row.get("Subcategory"))
            sub_subcategory = clean_val(row.get("Sub_Subcategory"))
            semester = clean_int(row.get("Semester"))
            year = clean_int(row.get("Year"))
            internal_exam = clean_int(row.get("Internal"))
            subject_code = clean_val(row.get("Subject_Code"))
            module = clean_int(row.get("Module"))
            title = clean_val(row.get("Title"))
            telegram_file_id = clean_val(row.get("Telegram_File_ID"))
            file_name = clean_val(row.get("File_Name"))

            # Map subject_code to subject_id FK (store None if subject_code is empty or unmapped)
            subject_id = subject_map.get(subject_code) if subject_code else None

            # Skip rows missing mandatory title or category
            if not category or not title:
                continue

            resources.append(
                (
                    category,
                    subcategory,
                    sub_subcategory,
                    subject_id,
                    semester,
                    year,
                    module,
                    internal_exam,
                    title,
                    file_name,
                    telegram_file_id,
                )
            )

    return resources


def seed_resources(file_path: str = "data/resources.csv") -> None:
    """
    Reads resources data from CSV and inserts records into PostgreSQL 'resources' table.
    Uses ON CONFLICT DO NOTHING for duplicate protection.
    """
    connection = get_db_connection()
    if connection is None:
        print("Failed to establish database connection. Seeding aborted.")
        return

    try:
        with connection.cursor() as cursor:
            # 1. Retrieve subject_code -> subject_id mapping
            subject_map = get_subject_mapping(cursor)

            # 2. Parse resources CSV
            resources_data = parse_resources_file(file_path, subject_map)

            # 3. Parameterized SQL query with ON CONFLICT clause
            insert_query = """
            INSERT INTO resources (
                category,
                subcategory,
                sub_subcategory,
                subject_id,
                semester,
                year,
                module,
                internal_exam,
                title,
                file_name,
                telegram_file_id
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (
                category, subcategory, sub_subcategory, subject_id, semester, year, module, internal_exam, title
            ) DO NOTHING;
            """

            # 4. Execute batch insertion
            cursor.executemany(insert_query, resources_data)

        # 5. Commit transaction
        connection.commit()
        print(f"Successfully processed {len(resources_data)} resources.")
    except Exception as error:
        if connection:
            connection.rollback()
        print(f"Error seeding resources table: {error}")
    finally:
        if connection:
            connection.close()
