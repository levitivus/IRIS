"""
app/services/resource_service.py

Service layer for querying subjects, creating resource records, and generating read-only resource analytics in PostgreSQL.
"""

from typing import Any, Dict, List, Optional, Tuple
import psycopg
from psycopg.errors import UniqueViolation

from app.database.connection import get_db_connection


def get_subjects_by_semester(semester: int) -> List[Dict[str, Any]]:
    """
    Fetches all subjects for a given semester from the subjects table.

    Returns:
        List[Dict[str, Any]]: List of subject records sorted by subject_code.
    """
    connection = get_db_connection()
    if connection is None:
        return []

    try:
        with connection.cursor() as cursor:
            query = """
            SELECT id, semester, subject_code, subject_name
            FROM subjects
            WHERE semester = %s
            ORDER BY subject_code ASC;
            """
            cursor.execute(query, (semester,))
            rows = cursor.fetchall()
            return [
                {
                    "id": row[0],
                    "semester": row[1],
                    "subject_code": row[2],
                    "subject_name": row[3],
                }
                for row in rows
            ]
    except Exception as error:
        print(f"Error fetching subjects for semester {semester}: {error}")
        return []
    finally:
        connection.close()


def get_subject_by_id(subject_id: int) -> Optional[Dict[str, Any]]:
    """
    Fetches a subject record by subject_id.
    """
    connection = get_db_connection()
    if connection is None:
        return None

    try:
        with connection.cursor() as cursor:
            query = """
            SELECT id, semester, subject_code, subject_name
            FROM subjects
            WHERE id = %s;
            """
            cursor.execute(query, (subject_id,))
            row = cursor.fetchone()
            if row:
                return {
                    "id": row[0],
                    "semester": row[1],
                    "subject_code": row[2],
                    "subject_name": row[3],
                }
            return None
    except Exception as error:
        print(f"Error fetching subject by id {subject_id}: {error}")
        return None
    finally:
        connection.close()


def create_resource(data: Dict[str, Any]) -> Tuple[bool, str, Optional[int]]:
    """
    Inserts a new resource record into PostgreSQL.

    Returns:
        Tuple[bool, str, Optional[int]]: (success, message, resource_id)
    """
    connection = get_db_connection()
    if connection is None:
        return False, "Database connection unavailable.", None

    try:
        with connection.cursor() as cursor:
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
            RETURNING id;
            """
            cursor.execute(
                insert_query,
                (
                    data.get("category"),
                    data.get("subcategory"),
                    data.get("sub_subcategory"),
                    data.get("subject_id"),
                    data.get("semester"),
                    data.get("year"),
                    data.get("module"),
                    data.get("internal_exam"),
                    data.get("title"),
                    data.get("file_name"),
                    data.get("telegram_file_id"),
                ),
            )
            resource_id = cursor.fetchone()[0]
        connection.commit()
        return True, "Resource uploaded and registered successfully.", resource_id
    except UniqueViolation:
        if connection:
            connection.rollback()
        return False, "⚠️ Duplicate Resource: An equivalent resource already exists in IRIS.", None
    except Exception as error:
        if connection:
            connection.rollback()
        print(f"Error creating resource: {error}")
        return False, f"Failed to save resource to database: {error}", None
    finally:
        if connection:
            connection.close()


def get_recent_resources(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Retrieves the latest uploaded resources ordered by uploaded_at DESC.
    """
    connection = get_db_connection()
    if connection is None:
        return []

    try:
        with connection.cursor() as cursor:
            query = """
            SELECT id, category, subcategory, sub_subcategory, title, file_name, uploaded_at
            FROM resources
            ORDER BY uploaded_at DESC, id DESC
            LIMIT %s;
            """
            cursor.execute(query, (limit,))
            rows = cursor.fetchall()
            return [
                {
                    "id": row[0],
                    "category": row[1],
                    "subcategory": row[2],
                    "sub_subcategory": row[3],
                    "title": row[4],
                    "file_name": row[5],
                    "uploaded_at": row[6],
                }
                for row in rows
            ]
    except Exception as error:
        print(f"Error fetching recent resources: {error}")
        return []
    finally:
        connection.close()


def get_resource_statistics() -> Dict[str, Any]:
    """
    Retrieves aggregate resource statistics, category counts, subject count, and latest upload info.
    """
    connection = get_db_connection()
    if connection is None:
        return {}

    try:
        with connection.cursor() as cursor:
            # 1. Total resources
            cursor.execute("SELECT COUNT(*) FROM resources;")
            total_resources = cursor.fetchone()[0]

            # 2. Count by category
            cursor.execute("SELECT category, COUNT(*) FROM resources GROUP BY category;")
            cat_counts = {row[0]: row[1] for row in cursor.fetchall()}

            # 3. Total subjects
            cursor.execute("SELECT COUNT(*) FROM subjects;")
            total_subjects = cursor.fetchone()[0]

            # 4. Latest upload
            cursor.execute("SELECT title, uploaded_at FROM resources ORDER BY uploaded_at DESC, id DESC LIMIT 1;")
            latest = cursor.fetchone()
            latest_title = latest[0] if latest else None
            latest_time = latest[1] if latest else None

            from app.utils.taxonomy import CATEGORIES
            category_breakdown = {cat: cat_counts.get(cat, 0) for cat in CATEGORIES}

            return {
                "total_resources": total_resources,
                "category_counts": category_breakdown,
                "total_subjects": total_subjects,
                "latest_title": latest_title,
                "latest_time": latest_time,
            }
    except Exception as error:
        print(f"Error fetching resource statistics: {error}")
        return {}
    finally:
        connection.close()
