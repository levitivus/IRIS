"""
app/services/admin_service.py

Service module for administrator authentication and retrieval from PostgreSQL.
"""

from typing import Any, Dict, Optional
from app.database.connection import get_db_connection


def get_admin(telegram_id: int) -> Optional[Dict[str, Any]]:
    """
    Retrieves administrator information from PostgreSQL by telegram_id.
    Only returns active administrators (is_active = TRUE).

    Args:
        telegram_id (int): Telegram User ID.

    Returns:
        Optional[Dict[str, Any]]: Admin dictionary if found and active, else None.
    """
    connection = get_db_connection()
    if connection is None:
        print("Error: Database connection unavailable in admin_service.")
        return None

    try:
        with connection.cursor() as cursor:
            query = """
            SELECT id, telegram_id, full_name, role, is_active, created_at
            FROM admins
            WHERE telegram_id = %s AND is_active = TRUE;
            """
            cursor.execute(query, (telegram_id,))
            row = cursor.fetchone()
            if row:
                return {
                    "id": row[0],
                    "telegram_id": row[1],
                    "full_name": row[2],
                    "role": row[3],
                    "is_active": row[4],
                    "created_at": row[5],
                }
            return None
    except Exception as error:
        print(f"Error querying admin table for telegram_id {telegram_id}: {error}")
        return None
    finally:
        connection.close()


def is_admin(telegram_id: int) -> bool:
    """
    Checks if a given Telegram ID belongs to an active administrator.

    Args:
        telegram_id (int): Telegram User ID.

    Returns:
        bool: True if the user is an active administrator, False otherwise.
    """
    admin = get_admin(telegram_id)
    return admin is not None
