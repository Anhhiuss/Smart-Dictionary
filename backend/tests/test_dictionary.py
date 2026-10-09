"""Unit tests for Word model, database persistence, and WordRepository."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.database.database import Base
from backend.app.models.word import Word
from backend.app.schemas.word import WordCreate, WordUpdate
from backend.app.repositories.word_repository import WordRepository


@pytest.fixture
def db_session():
    """In-memory SQLite session fixture for isolated testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


def test_create_and_get_word(db_session):
    """Test inserting a new word and fetching by word and id."""
    repo = WordRepository(db_session)
    word_in = WordCreate(
        word="  algorithm  ",
        meaning="thuật toán",
        pronunciation="/ˈæl.ɡə.rɪ.ðəm/",
        word_type="noun",
        example="An algorithm solves problems.",
    )
    created = repo.create(word_in)
    assert created.id is not None
    assert created.word == "algorithm"
    assert created.meaning == "thuật toán"

    # Get by word
    fetched = repo.get_by_word("ALGORITHM")
    assert fetched is not None
    assert fetched.id == created.id

    # Get by ID
    fetched_by_id = repo.get_by_id(created.id)
    assert fetched_by_id is not None
    assert fetched_by_id.word == "algorithm"


def test_update_word(db_session):
    """Test modifying existing word attributes."""
    repo = WordRepository(db_session)
    created = repo.create(WordCreate(word="loop", meaning="vòng lặp", word_type="noun"))

    updated = repo.update(
        created.id,
        WordUpdate(meaning="vòng lặp trong lập trình", example="A while loop runs until false."),
    )
    assert updated is not None
    assert updated.meaning == "vòng lặp trong lập trình"
    assert updated.example == "A while loop runs until false."


def test_delete_word(db_session):
    """Test deleting an existing word record."""
    repo = WordRepository(db_session)
    created = repo.create(WordCreate(word="temp", meaning="tạm thời"))
    word_id = created.id

    assert repo.delete(word_id) is True
    assert repo.get_by_id(word_id) is None
    assert repo.delete(word_id) is False


def test_list_and_count_words(db_session):
    """Test pagination and filtering."""
    repo = WordRepository(db_session)
    repo.create(WordCreate(word="stack", meaning="ngăn xếp"))
    repo.create(WordCreate(word="queue", meaning="hàng đợi"))
    repo.create(WordCreate(word="state", meaning="trạng thái"))

    assert repo.count() == 3
    assert repo.count(search_filter="sta") == 2

    words = repo.list(skip=0, limit=2)
    assert len(words) == 2
