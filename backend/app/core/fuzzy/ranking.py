"""Deterministic, explainable ranking engine for approximate and fuzzy search results.

Academic Ranking Principles:
    Rather than opaque heuristic weights or machine learning models, results
    are sorted using an explicit multi-attribute lexicographical key:

    Key Tuple: (is_exact, is_prefix, edit_distance, length_diff, word)

Criteria Hierarchy:
    1. Exact Match Priority (is_exact):
       Distance == 0 candidates rank highest (0 comes before 1).
    2. Prefix Match Advantage (is_prefix):
       Candidates where the target word begins with the query string receive
       priority over arbitrary mid-string edits (0 comes before 1).
    3. Minimal Edit Distance (edit_distance):
       Smaller Levenshtein distance precedes larger distance (1 before 2 before 3).
    4. Length Proximity (length_diff):
       Candidates with string length closer to the query length (|len(W) - len(Q)|)
       are preferred when distances are tied.
    5. Deterministic Lexicographical Order (word):
       Alphabetical sorting ensures consistent, reproducible results across runs.
"""

from typing import Any, Dict, List, NamedTuple, Optional


class RankedCandidate(NamedTuple):
    """Container for a candidate word evaluated during fuzzy search."""

    word: str
    distance: int
    payload: Optional[Any] = None


def compute_ranking_key(query: str, word: str, distance: int) -> tuple:
    """Computes the 5-tier deterministic comparison key for a candidate word."""
    is_exact = 0 if distance == 0 else 1
    is_prefix = 0 if word.startswith(query) else 1
    length_diff = abs(len(word) - len(query))
    return (is_exact, is_prefix, distance, length_diff, word)


def rank_candidates(
    query: str,
    candidates: List[RankedCandidate],
    limit: Optional[int] = None,
) -> List[RankedCandidate]:
    """Ranks candidate words deterministically based on multi-attribute criteria.

    Args:
        query: The normalized search query string.
        candidates: List of RankedCandidate instances with computed edit distances.
        limit: Optional maximum number of top candidates to return.

    Returns:
        Sorted list of RankedCandidate instances, sliced up to limit if specified.
    """
    if not candidates:
        return []

    # Sort using explicit 5-tier tuple
    sorted_candidates = sorted(
        candidates,
        key=lambda c: compute_ranking_key(query, c.word, c.distance),
    )

    if limit is not None and limit > 0:
        return sorted_candidates[:limit]

    return sorted_candidates
