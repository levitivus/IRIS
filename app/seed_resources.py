"""
app/seed_resources.py

Runner script to execute PostgreSQL resources table seeding for IRIS.
"""

from app.database.seed_resources import seed_resources

if __name__ == "__main__":
    seed_resources()
