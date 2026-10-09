"""Unit tests auditing Unicode normalization, Vietnamese diacritics, and NFC/NFD equivalence."""

import unicodedata
import pytest
from backend.app.core.trie.trie import Trie
from backend.app.core.fuzzy.levenshtein import (
    levenshtein_distance,
    levenshtein_matrix,
    normalize_string,
)
from backend.app.core.fuzzy.fuzzy_search import fuzzy_search
from backend.app.schemas.word import WordCreate


# ---------------------------------------------------------------------------
# Test 1: Composed (NFC) vs Decomposed (NFD) Equivalences
# ---------------------------------------------------------------------------

def test_nfc_nfd_equivalence_in_normalization():
    """Verify that normalize_string normalizes both NFC and NFD strings to identical forms."""
    vietnamese_word = "tiếng việt"
    nfc_word = unicodedata.normalize("NFC", vietnamese_word)
    nfd_word = unicodedata.normalize("NFD", vietnamese_word)

    # Raw strings have different length and code points
    assert nfc_word != nfd_word
    assert len(nfc_word) == 10
    assert len(nfd_word) == 14

    # Normalized strings must be identical in NFC canonical form
    assert normalize_string(nfc_word) == normalize_string(nfd_word)
    assert Trie.normalize(nfc_word) == Trie.normalize(nfd_word)


def test_levenshtein_nfc_nfd_distance_is_zero():
    """Verify that edit distance between composed and decomposed representations is 0."""
    word = "thuật toán"
    nfc = unicodedata.normalize("NFC", word)
    nfd = unicodedata.normalize("NFD", word)

    assert levenshtein_distance(nfc, nfd) == 0


def test_trie_search_with_decomposed_input():
    """Verify that inserting in NFC allows lookup via NFD input and vice versa."""
    trie = Trie()
    word_nfc = unicodedata.normalize("NFC", "từ điển")
    word_nfd = unicodedata.normalize("NFD", "từ điển")

    trie.insert(word_nfc, 1)

    # Exact search using NFD query
    found, word_id = trie.search(word_nfd)
    assert found is True
    assert word_id == 1

    # Prefix lookup using NFD prefix
    prefix_nfd = unicodedata.normalize("NFD", "từ")
    assert trie.starts_with(prefix_nfd) is True
    suggestions = trie.get_suggestions(prefix_nfd)
    assert suggestions == [word_nfc]


def test_fuzzy_search_with_decomposed_query():
    """Verify fuzzy search properly matches when query is in NFD format."""
    vocab = [unicodedata.normalize("NFC", "thuật toán")]
    query_nfd = unicodedata.normalize("NFD", "thuật toán")

    results = fuzzy_search(query_nfd, vocab, max_distance=1)
    assert len(results) == 1
    assert results[0].word == unicodedata.normalize("NFC", "thuật toán")
    assert results[0].distance == 0


# ---------------------------------------------------------------------------
# Test 2: Uppercase vs Lowercase and Case Folding
# ---------------------------------------------------------------------------

def test_case_insensitivity_with_diacritics():
    """Verify uppercase Vietnamese characters fold to canonical lowercase."""
    upper = "TIẾNG VIỆT"
    lower = "tiếng việt"

    assert normalize_string(upper) == normalize_string(lower)
    assert Trie.normalize(upper) == Trie.normalize(lower)
    assert levenshtein_distance(upper, lower) == 0


# ---------------------------------------------------------------------------
# Test 3: Diacritics Preservation
# ---------------------------------------------------------------------------

def test_vietnamese_diacritics_are_strictly_preserved():
    """Ensure diacritics are NOT stripped (e.g. 'máy tính' != 'may tinh')."""
    with_accents = "máy tính"
    without_accents = "may tinh"

    # Must NOT be normalized to identical strings
    assert normalize_string(with_accents) != normalize_string(without_accents)

    # Edit distance should reflect the character substitutions (á -> a, í -> i)
    dist = levenshtein_distance(with_accents, without_accents)
    assert dist == 2  # 2 substitutions


# ---------------------------------------------------------------------------
# Test 4: Empty and Whitespace Queries
# ---------------------------------------------------------------------------

def test_empty_and_whitespace_across_all_components():
    """Empty and whitespace-only queries must produce safe, uniform empty responses."""
    test_inputs = ["", "   ", "\t\n  "]

    trie = Trie()
    trie.insert("test", 1)

    for inp in test_inputs:
        assert normalize_string(inp) == ""
        assert Trie.normalize(inp) == ""
        assert trie.search(inp) == (False, None)
        assert trie.starts_with(inp) is False
        assert trie.get_suggestions(inp) == []
        assert trie.delete(inp) is False
        assert fuzzy_search(inp, ["test"]) == []
        assert levenshtein_distance(inp, "") == 0
        assert levenshtein_distance(inp, "a") == 1
