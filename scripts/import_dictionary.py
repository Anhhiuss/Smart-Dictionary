"""Command-line script to import data/dictionary.json into SQLite."""

import sys
import time
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.database.database import init_db, SessionLocal
from backend.app.database.seed import seed_dictionary


def main():
    print("=" * 60)
    print("Smart Dictionary — Dataset Import Utility")
    print("=" * 60)

    start_time = time.perf_counter()

    print("[1/2] Initializing database tables...")
    init_db()

    print("[2/2] Importing entries from data/dictionary.json...")
    db = SessionLocal()
    try:
        imported, skipped, invalid = seed_dictionary(db=db)
        elapsed = time.perf_counter() - start_time

        print("-" * 60)
        print(f"Import Summary:")
        print(f"  • Successfully imported: {imported:,} words")
        print(f"  • Skipped (duplicates):  {skipped:,} words")
        print(f"  • Invalid entries:       {invalid:,} words")
        print(f"  • Execution time:        {elapsed:.3f} seconds")
        print("-" * 60)
    except Exception as e:
        print(f"[ERROR] Import failed: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
