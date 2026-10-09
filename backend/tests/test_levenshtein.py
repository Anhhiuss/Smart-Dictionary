"""Unit tests for manual Levenshtein Distance dynamic programming implementation."""

import pytest
from backend.app.core.fuzzy.levenshtein import (
    levenshtein_distance,
    levenshtein_matrix,
    normalize_string,
)


# ---------------------------------------------------------------------------
# Core Academic Test Cases Specified in Requirements
# ---------------------------------------------------------------------------

def test_identical_empty_strings():
    """Test: '' vs '' => 0."""
    assert levenshtein_distance("", "") == 0
    matrix = levenshtein_matrix("", "")
    assert matrix == [[0]]


def test_identical_non_empty_strings():
    """Test: 'cat' vs 'cat' => 0."""
    assert levenshtein_distance("cat", "cat") == 0


def test_single_substitution():
    """Test: 'cat' vs 'bat' => 1 (substitute 'c' with 'b')."""
    assert levenshtein_distance("cat", "bat") == 1


def test_single_insertion():
    """Test: 'cat' vs 'cats' => 1 (insert 's')."""
    assert levenshtein_distance("cat", "cats") == 1


def test_single_deletion():
    """Test: 'cats' vs 'cat' => 1 (delete 's')."""
    assert levenshtein_distance("cats", "cat") == 1


def test_classic_kitten_sitting():
    """Test: 'kitten' vs 'sitting' => 3.

    k -> s (substitution: 1)
    e -> i (substitution: 2)
    insert 'g' at the end (insertion: 3)
    """
    assert levenshtein_distance("kitten", "sitting") == 3


# ---------------------------------------------------------------------------
# Detailed Dynamic Programming Matrix Verification
# ---------------------------------------------------------------------------

def test_levenshtein_matrix_dimensions_and_base_cases():
    """Verify that DP table shape is (M+1) x (N+1) and base rows/columns match lengths."""
    s1 = "abc"
    s2 = "defg"
    matrix = levenshtein_matrix(s1, s2)

    assert len(matrix) == 4      # M + 1 = 3 + 1
    assert len(matrix[0]) == 5   # N + 1 = 4 + 1

    # Base column D[i][0] == i
    for i in range(4):
        assert matrix[i][0] == i

    # Base row D[0][j] == j
    for j in range(5):
        assert matrix[0][j] == j

    # Bottom-right cell equals the distance
    assert matrix[3][4] == levenshtein_distance(s1, s2)


def test_symmetry():
    """Test that Levenshtein distance is symmetric: dist(A, B) == dist(B, A)."""
    pairs = [
        ("apple", "aple"),
        ("computer", "comptuer"),
        ("algorithm", "logarithm"),
        ("structure", "structures"),
        ("database", "data"),
    ]
    for w1, w2 in pairs:
        assert levenshtein_distance(w1, w2) == levenshtein_distance(w2, w1)


def test_case_normalization():
    """Test that case normalization operates uniformly."""
    assert levenshtein_distance("  CoMpUtEr  ", "computer") == 0
    assert levenshtein_distance("CAT", "cat") == 0
    assert levenshtein_distance("APPLE", "APLE") == 1

    # Without normalization flag, cases should differ
    assert levenshtein_distance("Cat", "cat", normalize=False) == 1


def test_empty_string_with_target():
    """Test empty string against non-empty string."""
    assert levenshtein_distance("", "python") == 6
    assert levenshtein_distance("python", "") == 6


def test_unicode_handling():
    """Test unicode characters support (e.g., Vietnamese diacritics)."""
    # 'từ điển' vs 'từ điên' (substitution of 'ể' with 'ê')
    assert levenshtein_distance("từ điển", "từ điên") == 1
    # 'thuật toán' vs 'thuật' (deletion of 5 chars including space)
    assert levenshtein_distance("thuật toán", "thuật") == 5


def test_triangular_inequality():
    """Verify metric property: dist(A, C) <= dist(A, B) + dist(B, C)."""
    a = "computer"
    b = "comptuer"
    c = "commuter"
    assert levenshtein_distance(a, c) <= (
        levenshtein_distance(a, b) + levenshtein_distance(b, c)
    )
