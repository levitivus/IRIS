"""
app/seed_subjects.py

Runner script to execute PostgreSQL subjects table seeding for IRIS.
"""

from app.database.seed_subjects import seed_subjects

if __name__ == "__main__":
    seed_subjects()
