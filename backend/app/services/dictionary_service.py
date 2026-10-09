"""Dictionary service orchestrating persistent CRUD operations and in-memory Trie synchronization."""

from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from backend.app.core.trie.trie import Trie
from backend.app.core.trie.trie_index import (
    deindex_vietnamese_phrases_for_word,
    get_trie_index,
    index_vietnamese_phrases_for_word,
)
from backend.app.models.word import Word
from backend.app.repositories.word_repository import WordRepository
from backend.app.schemas.word import WordCreate, WordUpdate


class WordAlreadyExistsError(ValueError):
    """Raised when attempting to insert or rename a word to an existing headword."""
    pass


class DictionaryService:
    """Business service handling dictionary CRUD and bidirectional Trie synchronization."""

    def __init__(self, db: Session, trie: Optional[Trie] = None):
        self.db = db
        self.repo = WordRepository(db)
        self.trie = trie or get_trie_index()

    def get_by_id(self, word_id: int) -> Optional[Word]:
        """Fetch word entity by primary key ID."""
        return self.repo.get_by_id(word_id)

    def get_by_word(self, word: str) -> Optional[Word]:
        """Fetch word entity by exact normalized headword string."""
        return self.repo.get_by_word(word)

    def list_words(
        self,
        skip: int = 0,
        limit: int = 50,
        search_filter: Optional[str] = None,
    ) -> Tuple[int, List[Word]]:
        """List words with pagination and optional substring filter.

        Returns:
            Tuple of (total_count, list_of_words).
        """
        total = self.repo.count(search_filter=search_filter)
        items = self.repo.list(skip=skip, limit=limit, search_filter=search_filter)
        return total, items

    def create_word(self, word_in: WordCreate) -> Word:
        """Creates a new word in persistent SQLite and synchronizes the Trie indices.

        Raises:
            WordAlreadyExistsError: If a word with this headword already exists.
        """
        existing = self.repo.get_by_word(word_in.word)
        if existing:
            raise WordAlreadyExistsError(f"Word '{word_in.word}' already exists in dictionary.")

        # Step 1: Persist in SQLite
        db_word = self.repo.create(word_in)

        # Step 2: Synchronize in-memory English headwords Trie index
        self.trie.insert(db_word.word, db_word.id)

        # Step 3: Synchronize Vietnamese phrases Trie index
        if db_word.meaning:
            index_vietnamese_phrases_for_word(db_word.id, db_word.meaning)

        return db_word

    def update_word(self, word_id: int, word_in: WordUpdate) -> Optional[Word]:
        """Updates an existing word and maintains Trie synchronization if the headword or meaning changes.

        Raises:
            WordAlreadyExistsError: If the new headword conflicts with another record.
        """
        existing = self.repo.get_by_id(word_id)
        if not existing:
            return None

        old_word = existing.word
        old_meaning = existing.meaning
        new_word = word_in.word
        new_meaning = word_in.meaning

        # If headword is being changed, verify uniqueness
        if new_word and new_word != old_word:
            conflict = self.repo.get_by_word(new_word)
            if conflict and conflict.id != word_id:
                raise WordAlreadyExistsError(f"Word '{new_word}' already exists in dictionary.")

        # Step 1: Update persistent record in SQLite
        updated_word = self.repo.update(word_id, word_in)
        if not updated_word:
            return None

        # Step 2: Synchronize English Trie if headword text changed
        if new_word and new_word != old_word:
            self.trie.delete(old_word)
            self.trie.insert(updated_word.word, updated_word.id)

        # Step 3: Synchronize Vietnamese phrases Trie if meaning text changed
        if new_meaning is not None and new_meaning != old_meaning:
            if old_meaning:
                deindex_vietnamese_phrases_for_word(word_id, old_meaning)
            if updated_word.meaning:
                index_vietnamese_phrases_for_word(word_id, updated_word.meaning)

        return updated_word

    def delete_word(self, word_id: int) -> bool:
        """Deletes a word from SQLite and prunes its entry from all Trie indices."""
        existing = self.repo.get_by_id(word_id)
        if not existing:
            return False

        word_text = existing.word
        meaning_text = existing.meaning

        # Step 1: Delete from SQLite
        deleted = self.repo.delete(word_id)
        if deleted:
            # Step 2: Synchronize English Trie
            self.trie.delete(word_text)
            # Step 3: Synchronize Vietnamese phrases Trie
            if meaning_text:
                deindex_vietnamese_phrases_for_word(word_id, meaning_text)

        return deleted
