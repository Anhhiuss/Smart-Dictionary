"""Unit tests for the Trie (Prefix Tree) data structure."""

import pytest
from backend.app.core.trie.trie import Trie
from backend.app.core.trie.trie_node import TrieNode


@pytest.fixture
def empty_trie() -> Trie:
    """Fixture providing a fresh empty Trie."""
    return Trie()


@pytest.fixture
def populated_trie() -> Trie:
    """Fixture providing a Trie populated with a standard set of words."""
    trie = Trie()
    words = [
        ("computer", 1),
        ("company", 2),
        ("complete", 3),
        ("compare", 4),
        ("computation", 5),
        ("apple", 6),
        ("apply", 7),
        ("application", 8),
        ("banana", 9),
    ]
    for word, word_id in words:
        trie.insert(word, word_id)
    return trie


# ---------------------------------------------------------------------------
# Test Cases 1 & 2: Insert one word and exact search
# ---------------------------------------------------------------------------

def test_insert_one_word_and_exact_search(empty_trie: Trie):
    """Test 1 & 2: Insert a single word and verify it can be found with correct word_id."""
    assert empty_trie.size == 0
    assert empty_trie.insert("computer", 101) is True
    assert empty_trie.size == 1

    found, word_id = empty_trie.search("computer")
    assert found is True
    assert word_id == 101


# ---------------------------------------------------------------------------
# Test Case 3: Search missing word
# ---------------------------------------------------------------------------

def test_search_missing_word(populated_trie: Trie):
    """Test 3: Search for non-existent words (subwords, superwords, completely unrelated)."""
    found, word_id = populated_trie.search("comp")
    assert found is False
    assert word_id is None

    found, word_id = populated_trie.search("computers")
    assert found is False
    assert word_id is None

    found, word_id = populated_trie.search("orange")
    assert found is False
    assert word_id is None


# ---------------------------------------------------------------------------
# Test Case 4: Prefix search (starts_with)
# ---------------------------------------------------------------------------

def test_starts_with(populated_trie: Trie):
    """Test 4: Verify starts_with accurately detects existing and non-existing prefixes."""
    assert populated_trie.starts_with("comp") is True
    assert populated_trie.starts_with("app") is True
    assert populated_trie.starts_with("ban") is True
    assert populated_trie.starts_with("c") is True
    assert populated_trie.starts_with("xyz") is False
    assert populated_trie.starts_with("compx") is False


# ---------------------------------------------------------------------------
# Test Case 5: Multiple words sharing prefix
# ---------------------------------------------------------------------------

def test_multiple_words_sharing_prefix(populated_trie: Trie):
    """Test 5: Verify get_suggestions retrieves all words starting with a shared prefix."""
    suggestions = populated_trie.get_suggestions("comp", limit=10)
    # Alphabetical order: company, compare, complete, computation, computer
    assert suggestions == [
        "company",
        "compare",
        "complete",
        "computation",
        "computer",
    ]


# ---------------------------------------------------------------------------
# Test Case 6: Suggestions with limit
# ---------------------------------------------------------------------------

def test_suggestions_with_limit(populated_trie: Trie):
    """Test 6: Verify suggestions list respects the limit parameter and deterministic order."""
    suggestions_limit_2 = populated_trie.get_suggestions("comp", limit=2)
    assert len(suggestions_limit_2) == 2
    assert suggestions_limit_2 == ["company", "compare"]

    suggestions_limit_3 = populated_trie.get_suggestions("app", limit=2)
    assert len(suggestions_limit_3) == 2
    assert suggestions_limit_3 == ["apple", "application"]


# ---------------------------------------------------------------------------
# Test Case 7: Duplicate insertion
# ---------------------------------------------------------------------------

def test_duplicate_insertion(empty_trie: Trie):
    """Test 7: Inserting the same word updates the word_id without incrementing size."""
    empty_trie.insert("python", 1)
    assert empty_trie.size == 1
    found, word_id = empty_trie.search("python")
    assert found is True
    assert word_id == 1

    # Insert duplicate with updated ID
    empty_trie.insert("python", 999)
    assert empty_trie.size == 1  # Size remains 1
    found, word_id = empty_trie.search("python")
    assert found is True
    assert word_id == 999


# ---------------------------------------------------------------------------
# Test Case 8: Delete leaf word
# ---------------------------------------------------------------------------

def test_delete_leaf_word(empty_trie: Trie):
    """Test 8: Deleting a leaf word prunes unshared nodes and decrements size."""
    empty_trie.insert("cat", 1)
    assert empty_trie.size == 1

    assert empty_trie.delete("cat") is True
    assert empty_trie.size == 0
    found, _ = empty_trie.search("cat")
    assert found is False
    # Root should have no children left because node was pruned
    assert len(empty_trie.root.children) == 0


# ---------------------------------------------------------------------------
# Test Case 9: Delete word that shares prefix with another word
# ---------------------------------------------------------------------------

def test_delete_shared_prefix_word(empty_trie: Trie):
    """Test 9: Deleting a word that shares prefix with another word preserves other word."""
    empty_trie.insert("car", 1)
    empty_trie.insert("card", 2)
    empty_trie.insert("care", 3)
    assert empty_trie.size == 3

    # Delete shorter prefix word 'car'
    assert empty_trie.delete("car") is True
    assert empty_trie.size == 2
    assert empty_trie.search("car") == (False, None)
    assert empty_trie.search("card") == (True, 2)
    assert empty_trie.search("care") == (True, 3)

    # Delete 'card'; 'care' must still exist
    assert empty_trie.delete("card") is True
    assert empty_trie.size == 1
    assert empty_trie.search("card") == (False, None)
    assert empty_trie.search("care") == (True, 3)


# ---------------------------------------------------------------------------
# Test Case 10: Delete missing word
# ---------------------------------------------------------------------------

def test_delete_missing_word(populated_trie: Trie):
    """Test 10: Deleting a missing word returns False and does not affect Trie size."""
    initial_size = populated_trie.size
    assert populated_trie.delete("nonexistent") is False
    assert populated_trie.delete("comp") is False  # Prefix exists, but not a full word
    assert populated_trie.size == initial_size


# ---------------------------------------------------------------------------
# Test Case 11: Empty input
# ---------------------------------------------------------------------------

def test_empty_input_handling(empty_trie: Trie):
    """Test 11: Empty string, whitespace-only, and None are handled gracefully."""
    assert empty_trie.insert("", 1) is False
    assert empty_trie.insert("   ", 1) is False
    assert empty_trie.size == 0

    assert empty_trie.search("") == (False, None)
    assert empty_trie.search("   ") == (False, None)
    assert empty_trie.starts_with("") is False
    assert empty_trie.starts_with("   ") is False
    assert empty_trie.get_suggestions("") == []
    assert empty_trie.get_suggestions("   ") == []
    assert empty_trie.delete("") is False
    assert empty_trie.delete("   ") is False


# ---------------------------------------------------------------------------
# Test Case 12: Case normalization
# ---------------------------------------------------------------------------

def test_case_normalization(empty_trie: Trie):
    """Test 12: Upper/mixed case and whitespace are normalized cleanly."""
    empty_trie.insert("  CoMpUtEr  ", 42)

    found, word_id = empty_trie.search("computer")
    assert found is True
    assert word_id == 42

    found, word_id = empty_trie.search("COMPUTER")
    assert found is True
    assert word_id == 42

    assert empty_trie.starts_with("COMP") is True
    suggestions = empty_trie.get_suggestions("CoMp", limit=5)
    assert suggestions == ["computer"]

    assert empty_trie.delete(" Computer ") is True
    assert empty_trie.search("computer") == (False, None)
    assert empty_trie.size == 0
