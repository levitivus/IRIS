"""
app/services/resource_service.py

Service layer for querying subjects, creating resource records, generating read-only resource analytics,
and handling student resource retrievals (Question Papers, Notes, Projects, Lab Manuals, Placement, Reference) in PostgreSQL.
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


# ==============================================================================
# STUDENT QUESTION PAPER RETRIEVAL SERVICE FUNCTIONS (PHASE 5)
# ==============================================================================

def get_qp_available_semesters(subcategory: str) -> List[int]:
    """
    Returns a sorted list of distinct semester numbers that have Question Paper resources for the given subcategory.
    """
    connection = get_db_connection()
    if connection is None:
        return []

    try:
        with connection.cursor() as cursor:
            query = """
            SELECT DISTINCT semester
            FROM resources
            WHERE category = 'Question Papers'
              AND subcategory = %s
              AND semester IS NOT NULL
            ORDER BY semester ASC;
            """
            cursor.execute(query, (subcategory,))
            return [row[0] for row in cursor.fetchall()]
    except Exception as error:
        print(f"Error fetching QP semesters for subcategory {subcategory}: {error}")
        return []
    finally:
        connection.close()


def get_qp_available_years(subcategory: str, semester: int) -> List[int]:
    """
    Returns a sorted list of distinct years for Question Paper resources matching subcategory and semester.
    """
    connection = get_db_connection()
    if connection is None:
        return []

    try:
        with connection.cursor() as cursor:
            query = """
            SELECT DISTINCT year
            FROM resources
            WHERE category = 'Question Papers'
              AND subcategory = %s
              AND semester = %s
              AND year IS NOT NULL
            ORDER BY year DESC;
            """
            cursor.execute(query, (subcategory, semester))
            return [row[0] for row in cursor.fetchall()]
    except Exception as error:
        print(f"Error fetching QP years for subcategory {subcategory}, sem {semester}: {error}")
        return []
    finally:
        connection.close()


def get_qp_available_internals(semester: int, year: int) -> List[int]:
    """
    Returns a sorted list of distinct internal exam integers (1 for First Internal, 2 for Second Internal)
    for Question Papers -> Internal Examination matching semester and year.
    """
    connection = get_db_connection()
    if connection is None:
        return []

    try:
        with connection.cursor() as cursor:
            query = """
            SELECT DISTINCT internal_exam
            FROM resources
            WHERE category = 'Question Papers'
              AND subcategory = 'Internal Examination'
              AND semester = %s
              AND year = %s
              AND internal_exam IS NOT NULL
            ORDER BY internal_exam ASC;
            """
            cursor.execute(query, (semester, year))
            return [row[0] for row in cursor.fetchall()]
    except Exception as error:
        print(f"Error fetching QP internals for sem {semester}, year {year}: {error}")
        return []
    finally:
        connection.close()


def get_qp_available_subjects(
    subcategory: str,
    semester: int,
    year: Optional[int] = None,
    internal_exam: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """
    Returns list of distinct subjects (id, semester, subject_code, subject_name) that have matching Question Paper resources.
    """
    connection = get_db_connection()
    if connection is None:
        return []

    try:
        with connection.cursor() as cursor:
            query = """
            SELECT DISTINCT s.id, s.semester, s.subject_code, s.subject_name
            FROM resources r
            JOIN subjects s ON r.subject_id = s.id
            WHERE r.category = 'Question Papers'
              AND r.subcategory = %s
              AND r.semester = %s
              AND (%s::integer IS NULL OR r.year = %s)
              AND (%s::integer IS NULL OR r.internal_exam = %s)
            ORDER BY s.subject_code ASC;
            """
            cursor.execute(
                query,
                (subcategory, semester, year, year, internal_exam, internal_exam),
            )
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
        print(f"Error fetching QP subjects: {error}")
        return []
    finally:
        connection.close()


def get_qp_resources(
    subcategory: str,
    semester: int,
    subject_id: int,
    year: Optional[int] = None,
    internal_exam: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """
    Retrieves matching Question Paper resource records from PostgreSQL.
    """
    connection = get_db_connection()
    if connection is None:
        return []

    try:
        with connection.cursor() as cursor:
            query = """
            SELECT r.id, r.category, r.subcategory, r.sub_subcategory, r.title, r.file_name, r.telegram_file_id
            FROM resources r
            WHERE r.category = 'Question Papers'
              AND r.subcategory = %s
              AND r.semester = %s
              AND r.subject_id = %s
              AND (%s::integer IS NULL OR r.year = %s)
              AND (%s::integer IS NULL OR r.internal_exam = %s)
            ORDER BY r.id DESC;
            """
            cursor.execute(
                query,
                (subcategory, semester, subject_id, year, year, internal_exam, internal_exam),
            )
            rows = cursor.fetchall()
            return [
                {
                    "id": row[0],
                    "category": row[1],
                    "subcategory": row[2],
                    "sub_subcategory": row[3],
                    "title": row[4],
                    "file_name": row[5],
                    "telegram_file_id": row[6],
                }
                for row in rows
            ]
    except Exception as error:
        print(f"Error fetching QP resources: {error}")
        return []
    finally:
        connection.close()


# ==============================================================================
# STUDENT NOTES RETRIEVAL SERVICE FUNCTIONS (PHASE 6)
# ==============================================================================

def get_notes_available_semesters() -> List[int]:
    """
    Returns a sorted list of distinct semester numbers that have Notes resources.
    """
    connection = get_db_connection()
    if connection is None:
        return []

    try:
        with connection.cursor() as cursor:
            query = """
            SELECT DISTINCT semester
            FROM resources
            WHERE category = 'Notes'
              AND semester IS NOT NULL
            ORDER BY semester ASC;
            """
            cursor.execute(query)
            return [row[0] for row in cursor.fetchall()]
    except Exception as error:
        print(f"Error fetching Notes semesters: {error}")
        return []
    finally:
        connection.close()


def get_notes_available_subjects(semester: int) -> List[Dict[str, Any]]:
    """
    Returns list of distinct subjects (id, semester, subject_code, subject_name) that have matching Notes resources.
    """
    connection = get_db_connection()
    if connection is None:
        return []

    try:
        with connection.cursor() as cursor:
            query = """
            SELECT DISTINCT s.id, s.semester, s.subject_code, s.subject_name
            FROM resources r
            JOIN subjects s ON r.subject_id = s.id
            WHERE r.category = 'Notes'
              AND r.semester = %s
            ORDER BY s.subject_code ASC;
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
        print(f"Error fetching Notes subjects for sem {semester}: {error}")
        return []
    finally:
        connection.close()


def get_notes_available_modules(semester: int, subject_id: int) -> List[int]:
    """
    Returns a sorted list of distinct module numbers (1-5) for Notes matching semester and subject_id.
    """
    connection = get_db_connection()
    if connection is None:
        return []

    try:
        with connection.cursor() as cursor:
            query = """
            SELECT DISTINCT module
            FROM resources
            WHERE category = 'Notes'
              AND semester = %s
              AND subject_id = %s
              AND module IS NOT NULL
            ORDER BY module ASC;
            """
            cursor.execute(query, (semester, subject_id))
            return [row[0] for row in cursor.fetchall()]
    except Exception as error:
        print(f"Error fetching Notes modules for sem {semester}, subject {subject_id}: {error}")
        return []
    finally:
        connection.close()


def get_notes_resources(semester: int, subject_id: int, module: int) -> List[Dict[str, Any]]:
    """
    Retrieves matching Notes resource records from PostgreSQL.
    """
    connection = get_db_connection()
    if connection is None:
        return []

    try:
        with connection.cursor() as cursor:
            query = """
            SELECT r.id, r.category, r.subcategory, r.sub_subcategory, r.title, r.file_name, r.telegram_file_id
            FROM resources r
            WHERE r.category = 'Notes'
              AND r.semester = %s
              AND r.subject_id = %s
              AND r.module = %s
            ORDER BY r.id DESC;
            """
            cursor.execute(query, (semester, subject_id, module))
            rows = cursor.fetchall()
            return [
                {
                    "id": row[0],
                    "category": row[1],
                    "subcategory": row[2],
                    "sub_subcategory": row[3],
                    "title": row[4],
                    "file_name": row[5],
                    "telegram_file_id": row[6],
                }
                for row in rows
            ]
    except Exception as error:
        print(f"Error fetching Notes resources: {error}")
        return []
    finally:
        connection.close()


# ==============================================================================
# STUDENT PHASE 7 RETRIEVAL SERVICE FUNCTIONS
# ==============================================================================

# --- PROJECTS ---

def get_projects_resources(subcategory: str, sub_subcategory: str) -> List[Dict[str, Any]]:
    """
    Retrieves matching Projects resource records from PostgreSQL.
    """
    connection = get_db_connection()
    if connection is None:
        return []

    try:
        with connection.cursor() as cursor:
            query = """
            SELECT r.id, r.category, r.subcategory, r.sub_subcategory, r.title, r.file_name, r.telegram_file_id
            FROM resources r
            WHERE r.category = 'Projects'
              AND r.subcategory = %s
              AND r.sub_subcategory = %s
            ORDER BY r.id DESC;
            """
            cursor.execute(query, (subcategory, sub_subcategory))
            rows = cursor.fetchall()
            return [
                {
                    "id": row[0],
                    "category": row[1],
                    "subcategory": row[2],
                    "sub_subcategory": row[3],
                    "title": row[4],
                    "file_name": row[5],
                    "telegram_file_id": row[6],
                }
                for row in rows
            ]
    except Exception as error:
        print(f"Error fetching Projects resources: {error}")
        return []
    finally:
        connection.close()


# --- LAB MANUALS ---

def get_lab_manuals_available_semesters(subcategory: str) -> List[int]:
    """
    Returns a sorted list of distinct semester numbers that have Lab Manuals resources for the given subcategory.
    """
    connection = get_db_connection()
    if connection is None:
        return []

    try:
        with connection.cursor() as cursor:
            query = """
            SELECT DISTINCT semester
            FROM resources
            WHERE category = 'Lab Manuals'
              AND subcategory = %s
              AND semester IS NOT NULL
            ORDER BY semester ASC;
            """
            cursor.execute(query, (subcategory,))
            return [row[0] for row in cursor.fetchall()]
    except Exception as error:
        print(f"Error fetching Lab Manuals semesters: {error}")
        return []
    finally:
        connection.close()


def get_lab_manuals_available_years(subcategory: str, semester: int) -> List[int]:
    """
    Returns a sorted list of distinct years for Lab Manuals resources matching subcategory and semester.
    """
    connection = get_db_connection()
    if connection is None:
        return []

    try:
        with connection.cursor() as cursor:
            query = """
            SELECT DISTINCT year
            FROM resources
            WHERE category = 'Lab Manuals'
              AND subcategory = %s
              AND semester = %s
              AND year IS NOT NULL
            ORDER BY year DESC;
            """
            cursor.execute(query, (subcategory, semester))
            return [row[0] for row in cursor.fetchall()]
    except Exception as error:
        print(f"Error fetching Lab Manuals years: {error}")
        return []
    finally:
        connection.close()


def get_lab_manuals_available_subjects(
    subcategory: str, semester: int, year: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Returns list of distinct subjects that have matching Lab Manuals resources.
    """
    connection = get_db_connection()
    if connection is None:
        return []

    try:
        with connection.cursor() as cursor:
            query = """
            SELECT DISTINCT s.id, s.semester, s.subject_code, s.subject_name
            FROM resources r
            JOIN subjects s ON r.subject_id = s.id
            WHERE r.category = 'Lab Manuals'
              AND r.subcategory = %s
              AND r.semester = %s
              AND (%s::integer IS NULL OR r.year = %s)
            ORDER BY s.subject_code ASC;
            """
            cursor.execute(query, (subcategory, semester, year, year))
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
        print(f"Error fetching Lab Manuals subjects: {error}")
        return []
    finally:
        connection.close()


def get_lab_manuals_resources(
    subcategory: str, semester: int, subject_id: int, year: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Retrieves matching Lab Manuals resource records from PostgreSQL.
    """
    connection = get_db_connection()
    if connection is None:
        return []

    try:
        with connection.cursor() as cursor:
            query = """
            SELECT r.id, r.category, r.subcategory, r.sub_subcategory, r.title, r.file_name, r.telegram_file_id
            FROM resources r
            WHERE r.category = 'Lab Manuals'
              AND r.subcategory = %s
              AND r.semester = %s
              AND r.subject_id = %s
              AND (%s::integer IS NULL OR r.year = %s)
            ORDER BY r.id DESC;
            """
            cursor.execute(query, (subcategory, semester, subject_id, year, year))
            rows = cursor.fetchall()
            return [
                {
                    "id": row[0],
                    "category": row[1],
                    "subcategory": row[2],
                    "sub_subcategory": row[3],
                    "title": row[4],
                    "file_name": row[5],
                    "telegram_file_id": row[6],
                }
                for row in rows
            ]
    except Exception as error:
        print(f"Error fetching Lab Manuals resources: {error}")
        return []
    finally:
        connection.close()


# --- PLACEMENT MATERIALS ---

def get_placement_resources(subcategory: str) -> List[Dict[str, Any]]:
    """
    Retrieves matching Placement Materials resource records from PostgreSQL.
    """
    connection = get_db_connection()
    if connection is None:
        return []

    try:
        with connection.cursor() as cursor:
            query = """
            SELECT r.id, r.category, r.subcategory, r.sub_subcategory, r.title, r.file_name, r.telegram_file_id
            FROM resources r
            WHERE r.category = 'Placement Materials'
              AND r.subcategory = %s
            ORDER BY r.id DESC;
            """
            cursor.execute(query, (subcategory,))
            rows = cursor.fetchall()
            return [
                {
                    "id": row[0],
                    "category": row[1],
                    "subcategory": row[2],
                    "sub_subcategory": row[3],
                    "title": row[4],
                    "file_name": row[5],
                    "telegram_file_id": row[6],
                }
                for row in rows
            ]
    except Exception as error:
        print(f"Error fetching Placement Materials resources: {error}")
        return []
    finally:
        connection.close()


# --- REFERENCE MATERIALS ---

def get_reference_available_years(subcategory: str, sub_subcategory: str) -> List[int]:
    """
    Returns a sorted list of distinct years for Reference Materials matching subcategory and sub_subcategory.
    """
    connection = get_db_connection()
    if connection is None:
        return []

    try:
        with connection.cursor() as cursor:
            query = """
            SELECT DISTINCT year
            FROM resources
            WHERE category = 'Reference Materials'
              AND subcategory = %s
              AND sub_subcategory = %s
              AND year IS NOT NULL
            ORDER BY year DESC;
            """
            cursor.execute(query, (subcategory, sub_subcategory))
            return [row[0] for row in cursor.fetchall()]
    except Exception as error:
        print(f"Error fetching Reference Materials years: {error}")
        return []
    finally:
        connection.close()


def get_reference_resources(
    subcategory: str, sub_subcategory: Optional[str] = None, year: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Retrieves matching Reference Materials resource records from PostgreSQL.
    """
    connection = get_db_connection()
    if connection is None:
        return []

    try:
        with connection.cursor() as cursor:
            query = """
            SELECT r.id, r.category, r.subcategory, r.sub_subcategory, r.title, r.file_name, r.telegram_file_id
            FROM resources r
            WHERE r.category = 'Reference Materials'
              AND r.subcategory = %s
              AND (%s::text IS NULL OR r.sub_subcategory = %s)
              AND (%s::integer IS NULL OR r.year = %s)
            ORDER BY r.id DESC;
            """
            cursor.execute(
                query,
                (subcategory, sub_subcategory, sub_subcategory, year, year),
            )
            rows = cursor.fetchall()
            return [
                {
                    "id": row[0],
                    "category": row[1],
                    "subcategory": row[2],
                    "sub_subcategory": row[3],
                    "title": row[4],
                    "file_name": row[5],
                    "telegram_file_id": row[6],
                }
                for row in rows
            ]
    except Exception as error:
        print(f"Error fetching Reference Materials resources: {error}")
        return []
    finally:
        connection.close()
