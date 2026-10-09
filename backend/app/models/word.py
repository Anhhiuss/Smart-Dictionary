"""SQLAlchemy ORM model for dictionary words."""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, CheckConstraint, Index
from backend.app.database.database import Base


class Word(Base):
    """Word entity representing a dictionary entry in persistent storage."""

    __tablename__ = "words"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    word = Column(String(100), unique=True, nullable=False, index=True)
    meaning = Column(Text, nullable=False)
    pronunciation = Column(String(100), nullable=True)
    word_type = Column(String(50), nullable=True)
    example = Column(Text, nullable=True)
    created_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    __table_args__ = (
        CheckConstraint("length(trim(word)) > 0", name="chk_word_not_empty"),
        Index("ix_words_word_lower", "word"),
    )

    def __repr__(self) -> str:
        return f"<Word(id={self.id}, word='{self.word}', type='{self.word_type}')>"
