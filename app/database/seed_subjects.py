"""
app/database/seed_subjects.py

Module responsible for reading data/subjects.txt, parsing subject entries across semesters,
and seeding the PostgreSQL 'subjects' table safely without duplicates.
"""

import os
import re
from typing import List, Tuple
from app.database.connection import get_db_connection

# Explicit mapping for entries that appear outside semester headings
SPECIAL_SEMESTERS = {
    "M24CA1M307": 3,
    "M24CA1I309": 3,
    "M24CA1P401": 4,
}


def parse_subjects_file(file_path: str = "data/subjects.txt") -> List[Tuple[int, str, str]]:
    """
    Reads and parses subjects.txt into a list of (semester, subject_code, subject_name) tuples.

    Args:
        file_path (str): Path to subjects.txt file. Defaults to "data/subjects.txt".

    Returns:
        List[Tuple[int, str, str]]: List of parsed subject tuples.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Subjects file not found: {file_path}")

    subjects = []
    current_semester = None

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line_str = line.strip()

            if not line_str or line_str.startswith("*"):
                continue

            # Detect SEMESTER headers (e.g. "SEMESTER 1")
            sem_match = re.match(r"^SEMESTER\s+(\d+)$", line_str, re.IGNORECASE)
            if sem_match:
                current_semester = int(sem_match.group(1))
                continue

            # Detect standalone project/internship section headers
            if any(header in line_str.upper() for header in ["MINI-PROJECT", "INTERNSHIP", "MAIN PROJECT"]):
                current_semester = None
                continue

            # Parse code and name separated by hyphen
            if " - " in line_str:
                parts = line_str.split(" - ", 1)
                code = parts[0].strip()
                name = parts[1].strip()
            else:
                code = line_str
                name = line_str

            # Determine semester using current_semester header or explicit SPECIAL_SEMESTERS mapping
            if current_semester is not None:
                sem = current_semester
            else:
                sem = SPECIAL_SEMESTERS.get(code, 0)

            subjects.append((sem, code, name))

    return subjects


def seed_subjects(file_path: str = "data/subjects.txt") -> None:
    """
    Reads subject data from data/subjects.txt and inserts records into PostgreSQL 'subjects' table.
    Uses ON CONFLICT (subject_code) DO NOTHING to prevent duplicate entries.
    """
    connection = get_db_connection()
    if connection is None:
        print("Failed to establish database connection. Seeding aborted.")
        return

    try:
        subjects_data = parse_subjects_file(file_path)
        insert_query = """
        INSERT INTO subjects (semester, subject_code, subject_name)
        VALUES (%s, %s, %s)
        ON CONFLICT (subject_code) DO NOTHING;
        """

        with connection.cursor() as cursor:
            cursor.executemany(insert_query, subjects_data)

        connection.commit()
        print(f"Successfully processed {len(subjects_data)} subjects.")
    except Exception as error:
        print(f"Error seeding subjects table: {error}")
    finally:
        connection.close()
