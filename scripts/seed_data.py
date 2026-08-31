import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.app.db.init_db import init_db

if __name__ == "__main__":
    print("Seeding database with benchmark records and user accounts...")
    init_db()
    print("Database seeding completed!")
