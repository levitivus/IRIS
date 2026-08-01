"""
app/seed_admins.py

Runner script to execute PostgreSQL admins table seeding for IRIS.
"""

from app.database.seed_admins import seed_admins

if __name__ == "__main__":
    seed_admins()
