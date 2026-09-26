"""
init_db.py
──────────
Initializes database schema and populates ModelMetric records.
"""

from app.db.database import engine, Base, SessionLocal
from app.db.models import ModelMetric
from migrate_db import migrate

def init_db():
    Base.metadata.create_all(bind=engine)
    migrate()

if __name__ == "__main__":
    init_db()
