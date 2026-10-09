"""Database seed module for populating SQLite from data/dictionary.json."""

import json
from pathlib import Path
from typing import Tuple
from sqlalchemy.orm import Session
from backend.app.database.database import SessionLocal, init_db
from backend.app.models.word import Word
from backend.app.schemas.word import WordCreate

DATA_FILE = Path(__file__).resolve().parent.parent.parent.parent / "data" / "dictionary.json"


def seed_dictionary(db: Session | None = None, file_path: Path | None = None) -> Tuple[int, int, int]:
    """Seed the SQLite database with dictionary entries from JSON.

    Returns:
        Tuple of (imported_count, skipped_count, invalid_count).
    """
    path = file_path or DATA_FILE
    if not path.exists():
        raise FileNotFoundError(f"Dictionary file not found at: {path}")

    with open(path, "r", encoding="utf-8") as f:
        entries = json.load(f)

    close_session = False
    if db is None:
        init_db()
        db = SessionLocal()
        close_session = True

    imported = 0
    skipped = 0
    invalid = 0

    try:
        # Pre-fetch existing words to guarantee fast deduplication
        existing_words = set(
            row[0] for row in db.query(Word.word).all()
        )

        to_insert = []
        for item in entries:
            try:
                # Validate input using Pydantic schema
                schema = WordCreate(
                    word=item.get("word", ""),
                    meaning=item.get("meaning", ""),
                    pronunciation=item.get("pronunciation"),
                    word_type=item.get("word_type"),
                    example=item.get("example"),
                )
            except Exception:
                invalid += 1
                continue

            normalized_word = schema.word
            if normalized_word in existing_words:
                skipped += 1
                continue

            to_insert.append(
                Word(
                    word=normalized_word,
                    meaning=schema.meaning,
                    pronunciation=schema.pronunciation,
                    word_type=schema.word_type,
                    example=schema.example,
                )
            )
            existing_words.add(normalized_word)
            imported += 1

        if to_insert:
            db.bulk_save_objects(to_insert)
            db.commit()

        return imported, skipped, invalid

    finally:
        if close_session:
            db.close()


if __name__ == "__main__":
    imported, skipped, invalid = seed_dictionary()
    print(f"Seed completed: {imported} imported, {skipped} skipped (duplicates), {invalid} invalid.")
