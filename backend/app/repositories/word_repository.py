"""Data access repository for Word entities in SQLite."""

from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from backend.app.models.word import Word
from backend.app.schemas.word import WordCreate, WordUpdate


class WordRepository:
    """Repository handling raw database CRUD operations on the words table."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, word_in: WordCreate) -> Word:
        """Create and persist a new word record."""
        db_word = Word(
            word=word_in.word.strip().lower(),
            meaning=word_in.meaning.strip(),
            pronunciation=word_in.pronunciation.strip() if word_in.pronunciation else None,
            word_type=word_in.word_type.strip().lower() if word_in.word_type else None,
            example=word_in.example.strip() if word_in.example else None,
        )
        self.db.add(db_word)
        self.db.commit()
        self.db.refresh(db_word)
        return db_word

    def get_by_id(self, word_id: int) -> Optional[Word]:
        """Retrieve word by primary key ID."""
        return self.db.get(Word, word_id)

    def get_by_word(self, word: str) -> Optional[Word]:
        """Retrieve word by exact normalized headword."""
        normalized = word.strip().lower()
        stmt = select(Word).where(Word.word == normalized)
        return self.db.scalars(stmt).first()

    def list(
        self,
        skip: int = 0,
        limit: int = 50,
        search_filter: Optional[str] = None,
    ) -> List[Word]:
        """List words with pagination and optional search filter."""
        stmt = select(Word)
        if search_filter:
            term = f"%{search_filter.strip().lower()}%"
            stmt = stmt.where(Word.word.like(term))
        stmt = stmt.order_by(Word.word.asc()).offset(skip).limit(limit)
        return list(self.db.scalars(stmt).all())

    def update(self, word_id: int, word_in: WordUpdate) -> Optional[Word]:
        """Update existing word record by ID."""
        db_word = self.get_by_id(word_id)
        if not db_word:
            return None

        update_data = word_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field == "word" and value is not None:
                setattr(db_word, field, value.strip().lower())
            elif field in ("meaning", "pronunciation", "example") and value is not None:
                setattr(db_word, field, value.strip())
            elif field == "word_type" and value is not None:
                setattr(db_word, field, value.strip().lower())
            else:
                setattr(db_word, field, value)

        self.db.commit()
        self.db.refresh(db_word)
        return db_word

    def delete(self, word_id: int) -> bool:
        """Delete word record by ID."""
        db_word = self.get_by_id(word_id)
        if not db_word:
            return False
        self.db.delete(db_word)
        self.db.commit()
        return True

    def count(self, search_filter: Optional[str] = None) -> int:
        """Count total words matching optional filter."""
        stmt = select(func.count(Word.id))
        if search_filter:
            term = f"%{search_filter.strip().lower()}%"
            stmt = stmt.where(Word.word.like(term))
        return self.db.scalar(stmt) or 0

    def get_all_words_minimal(self) -> List[Tuple[int, str]]:
        """Retrieve (id, word) for all records to facilitate in-memory Trie indexing."""
        stmt = select(Word.id, Word.word).order_by(Word.id.asc())
        return list(self.db.execute(stmt).all())

    def get_all_words_with_meanings(self) -> List[Tuple[int, str, str]]:
        """Retrieve (id, word, meaning) for all records to facilitate Vietnamese Trie and vocabulary indexing."""
        stmt = select(Word.id, Word.word, Word.meaning).order_by(Word.id.asc())
        return list(self.db.execute(stmt).all())

    def get_all_words_for_fuzzy(self) -> List[Tuple[str, dict]]:
        """Retrieve (word, payload) for all records to facilitate approximate fuzzy search."""
        stmt = select(
            Word.word,
            Word.id,
            Word.meaning,
            Word.pronunciation,
            Word.word_type,
        ).order_by(Word.word.asc())
        rows = self.db.execute(stmt).all()
        return [
            (
                row[0],
                {
                    "id": row[1],
                    "meaning": row[2],
                    "pronunciation": row[3],
                    "word_type": row[4],
                },
            )
            for row in rows
        ]
