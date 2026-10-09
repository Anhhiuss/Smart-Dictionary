"""Global in-memory Trie indices (English headwords & Vietnamese meanings) and lifecycle hydration."""

from typing import Dict, List, Optional, Set
from sqlalchemy.orm import Session
from backend.app.core.fuzzy.levenshtein import strip_vietnamese_diacritics
from backend.app.core.trie.trie import Trie
from backend.app.core.vietnamese.tokenizer import extract_vietnamese_phrases
from backend.app.repositories.word_repository import WordRepository

# Global in-memory English headwords Trie
_trie_instance: Optional[Trie] = None

# Global in-memory Vietnamese meaning phrases Trie
_vi_trie_instance: Optional[Trie] = None

# Inverted index: maps normalized Vietnamese phrase -> Set of word IDs
_vi_phrase_to_word_ids: Dict[str, Set[int]] = {}

# Inverted index: maps unaccented Vietnamese phrase -> Set of accented phrases
_vi_unaccent_to_accented: Dict[str, Set[str]] = {}


def get_trie_index() -> Trie:
    """Returns the singleton in-memory English headwords Trie instance."""
    global _trie_instance
    if _trie_instance is None:
        _trie_instance = Trie()
    return _trie_instance


def set_trie_index(trie: Trie) -> None:
    """Overrides the global English Trie instance (useful for testing)."""
    global _trie_instance
    _trie_instance = trie


def get_vietnamese_trie_index() -> Trie:
    """Returns the singleton in-memory Vietnamese meaning phrases Trie instance."""
    global _vi_trie_instance
    if _vi_trie_instance is None:
        _vi_trie_instance = Trie()
    return _vi_trie_instance


def set_vietnamese_trie_index(trie: Trie) -> None:
    """Overrides the global Vietnamese Trie instance (useful for testing)."""
    global _vi_trie_instance
    _vi_trie_instance = trie


def get_vi_phrase_to_word_ids() -> Dict[str, Set[int]]:
    """Returns the mapping from Vietnamese phrases to matched word IDs."""
    return _vi_phrase_to_word_ids


def get_vi_unaccent_to_accented() -> Dict[str, Set[str]]:
    """Returns the mapping from unaccented Vietnamese phrases to accented canonical phrases."""
    return _vi_unaccent_to_accented


def index_vietnamese_phrases_for_word(word_id: int, meaning: str) -> None:
    """Indexes Vietnamese phrases for a single word record into Trie and inverted mappings."""
    vi_trie = get_vietnamese_trie_index()
    phrases = extract_vietnamese_phrases(meaning)

    for phrase in phrases:
        # Insert phrase into Vietnamese Trie with arbitrary ID (phrase lookup returns True)
        vi_trie.insert(phrase, word_id)

        # Update phrase to word_ids map
        if phrase not in _vi_phrase_to_word_ids:
            _vi_phrase_to_word_ids[phrase] = set()
        _vi_phrase_to_word_ids[phrase].add(word_id)

        # Update unaccented map
        unaccented = strip_vietnamese_diacritics(phrase)
        if unaccented:
            if unaccented not in _vi_unaccent_to_accented:
                _vi_unaccent_to_accented[unaccented] = set()
            _vi_unaccent_to_accented[unaccented].add(phrase)


def deindex_vietnamese_phrases_for_word(word_id: int, old_meaning: str) -> None:
    """Prunes Vietnamese phrases for a deleted or updated word record."""
    vi_trie = get_vietnamese_trie_index()
    old_phrases = extract_vietnamese_phrases(old_meaning)

    for phrase in old_phrases:
        if phrase in _vi_phrase_to_word_ids:
            _vi_phrase_to_word_ids[phrase].discard(word_id)
            if not _vi_phrase_to_word_ids[phrase]:
                # No other words share this phrase: prune from Trie and mappings
                del _vi_phrase_to_word_ids[phrase]
                vi_trie.delete(phrase)

                unaccented = strip_vietnamese_diacritics(phrase)
                if unaccented in _vi_unaccent_to_accented:
                    _vi_unaccent_to_accented[unaccented].discard(phrase)
                    if not _vi_unaccent_to_accented[unaccented]:
                        del _vi_unaccent_to_accented[unaccented]


def hydrate_trie_from_db(db: Session, trie: Optional[Trie] = None) -> int:
    """Reads all words from SQLite and populates both English and Vietnamese Trie indices.

    Returns:
        Total count of English headwords indexed.
    """
    en_trie = trie or get_trie_index()
    en_trie.clear()

    vi_trie = get_vietnamese_trie_index()
    vi_trie.clear()
    _vi_phrase_to_word_ids.clear()
    _vi_unaccent_to_accented.clear()

    repo = WordRepository(db)
    records = repo.get_all_words_with_meanings()

    for word_id, word, meaning in records:
        en_trie.insert(word, word_id)
        if meaning:
            index_vietnamese_phrases_for_word(word_id, meaning)

    return en_trie.size
