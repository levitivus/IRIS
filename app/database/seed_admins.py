"""
app/database/seed_admins.py

Module responsible for seeding initial administrator accounts into the PostgreSQL 'admins' table.
"""

from app.database.connection import get_db_connection

SEED_ADMIN_QUERY = """
INSERT INTO admins (telegram_id, full_name, role, is_active)
VALUES (%s, %s, %s, %s)
ON CONFLICT (telegram_id) DO NOTHING;
"""


def seed_admins(
    telegram_id: int = 1116201482,
    full_name: str = "Rasputin",
    role: str = "super_admin",
    is_active: bool = True,
) -> None:
    """
    Inserts an initial administrator into the PostgreSQL 'admins' table if it does not already exist.
    """
    connection = get_db_connection()
    if connection is None:
        print("Failed to establish database connection. Admin seeding aborted.")
        return

    try:
        with connection.cursor() as cursor:
            cursor.execute(SEED_ADMIN_QUERY, (telegram_id, full_name, role, is_active))
        connection.commit()
        print("Initial administrator seeded successfully.")
    except Exception as error:
        if connection:
            connection.rollback()
        print(f"Error seeding administrator table: {error}")
    finally:
        if connection:
            connection.close()
