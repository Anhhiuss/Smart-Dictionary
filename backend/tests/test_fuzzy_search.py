"""Unit tests for the complete fuzzy search and candidate filtering pipeline."""

import pytest
from backend.app.core.fuzzy.fuzzy_search import fuzzy_search


@pytest.fixture
def sample_vocabulary():
    """Sample dictionary vocabulary covering tech and common terms."""
    return [
        "computer",
        "computation",
        "company",
        "compare",
        "complete",
        "commuter",
        "algorithm",
        "logarithm",
        "binary",
        "database",
        "array",
        "apple",
        "apply",
        "application",
    ]


def test_exact_word_ranks_first(sample_vocabulary):
    """When query is exact, it must be the first candidate with distance 0."""
    results = fuzzy_search("computer", sample_vocabulary, max_distance=2, limit=5)
    assert len(results) >= 1
    assert results[0].word == "computer"
    assert results[0].distance == 0


def test_obvious_typo_finds_intended_word(sample_vocabulary):
    """Test typo 'comptuer' successfully matches 'computer' (transposition / distance 2)."""
    results = fuzzy_search("comptuer", sample_vocabulary, max_distance=2, limit=5)
    result_words = [r.word for r in results]
    assert "computer" in result_words
    # Top suggestion must be computer
    assert results[0].word == "computer"
    assert results[0].distance == 2


def test_max_distance_threshold_is_respected(sample_vocabulary):
    """Words with edit distance > max_distance must NOT be included."""
    # Query 'app' with max_distance = 1:
    # 'apple' has dist 2 ('app' -> 'appl' -> 'apple') -> should be excluded
    # 'apply' has dist 2 -> should be excluded
    results_dist_1 = fuzzy_search("app", sample_vocabulary, max_distance=1)
    for r in results_dist_1:
        assert r.distance <= 1

    # With max_distance = 2, 'apple' and 'apply' should appear
    results_dist_2 = fuzzy_search("app", sample_vocabulary, max_distance=2)
    words_dist_2 = [r.word for r in results_dist_2]
    assert "apple" in words_dist_2 or "apply" in words_dist_2


def test_limit_is_respected(sample_vocabulary):
    """Verify limit parameter bounds returned list."""
    results = fuzzy_search("comp", sample_vocabulary, max_distance=3, limit=3)
    assert len(results) <= 3


def test_results_are_deterministic(sample_vocabulary):
    """Multiple invocations must produce identical ordering."""
    run1 = fuzzy_search("comptuer", sample_vocabulary, max_distance=2, limit=5)
    run2 = fuzzy_search("comptuer", sample_vocabulary, max_distance=2, limit=5)
    assert [r.word for r in run1] == [r.word for r in run2]
    assert [r.distance for r in run1] == [r.distance for r in run2]


def test_empty_query_behavior(sample_vocabulary):
    """Empty query, whitespace-only, or empty vocabulary returns empty list."""
    assert fuzzy_search("", sample_vocabulary) == []
    assert fuzzy_search("   ", sample_vocabulary) == []
    assert fuzzy_search("computer", []) == []


def test_no_duplicate_results():
    """Ensure duplicate words in input vocabulary are de-duplicated cleanly."""
    vocab_with_duplicates = ["computer", "computer", "computer", "commuter"]
    results = fuzzy_search("computer", vocab_with_duplicates, max_distance=2)
    words = [r.word for r in results]
    assert len(words) == len(set(words))
    assert words[0] == "computer"


def test_candidate_with_payload():
    """Test that vocabulary tuples (word, payload) preserve payloads through ranking."""
    vocab_with_payloads = [
        ("computer", {"id": 101, "meaning": "máy tính"}),
        ("commuter", {"id": 102, "meaning": "người đi vé tháng"}),
    ]
    results = fuzzy_search("comptuer", vocab_with_payloads, max_distance=2)
    assert len(results) >= 1
    assert results[0].word == "computer"
    assert results[0].payload == {"id": 101, "meaning": "máy tính"}
