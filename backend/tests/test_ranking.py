"""Unit tests for deterministic ranking logic."""

import pytest
from backend.app.core.fuzzy.ranking import (
    RankedCandidate,
    compute_ranking_key,
    rank_candidates,
)


def test_exact_match_highest_priority():
    """Verify that an exact match (distance 0) always ranks ahead of typo candidates."""
    candidates = [
        RankedCandidate("computers", 1),
        RankedCandidate("computer", 0),
        RankedCandidate("commuter", 2),
    ]
    ranked = rank_candidates("computer", candidates)
    assert ranked[0].word == "computer"
    assert ranked[0].distance == 0


def test_prefix_match_advantage():
    """Candidates that begin with query have priority when edit distances are equal."""
    query = "comp"
    # Both distance 1 from 'comp':
    # 'camp' -> substitution of 'o' for 'a' (distance 1, does NOT start with 'comp')
    # 'compx' -> insertion of 'x' (distance 1, DOES start with 'comp')
    candidates = [
        RankedCandidate("camp", 1),
        RankedCandidate("compx", 1),
    ]
    ranked = rank_candidates(query, candidates)
    assert ranked[0].word == "compx"
    assert ranked[1].word == "camp"


def test_smaller_edit_distance_precedes_larger():
    """Candidates with distance 1 must rank before candidates with distance 2."""
    candidates = [
        RankedCandidate("commuter", 2),
        RankedCandidate("compter", 1),
        RankedCandidate("computation", 4),
    ]
    ranked = rank_candidates("computer", candidates)
    assert [c.word for c in ranked] == ["compter", "commuter", "computation"]


def test_length_proximity_tie_breaker():
    """When distances and prefix status match, candidate closer in length to query ranks higher."""
    query = "graph"  # len = 5
    # Both distance 1, neither starts with 'graph':
    # 'grap'  (len 4, diff = 1)
    # 'graphs' (starts with 'graph', so prefix matches! Let's choose two that don't match prefix)
    # 'fraph' (len 5, diff = 0)
    # 'frape' (len 5, diff = 0) vs 'frap' (len 4, diff = 1)
    c1 = RankedCandidate("frap", 2)   # len 4, diff = 1
    c2 = RankedCandidate("fraph", 2)  # len 5, diff = 0
    ranked = rank_candidates(query, [c1, c2])
    assert ranked[0].word == "fraph"
    assert ranked[1].word == "frap"


def test_alphabetical_tie_breaker():
    """When all metrics are equal, alphabetical order breaks the tie deterministically."""
    query = "bat"
    candidates = [
        RankedCandidate("cat", 1),
        RankedCandidate("fat", 1),
        RankedCandidate("hat", 1),
        RankedCandidate("mat", 1),
    ]
    ranked = rank_candidates(query, candidates)
    assert [c.word for c in ranked] == ["cat", "fat", "hat", "mat"]


def test_ranking_with_limit():
    """Verify limit parameter properly slices top ranked candidates."""
    candidates = [
        RankedCandidate("a", 1),
        RankedCandidate("b", 1),
        RankedCandidate("c", 1),
        RankedCandidate("d", 1),
    ]
    ranked = rank_candidates("x", candidates, limit=2)
    assert len(ranked) == 2
    assert [c.word for c in ranked] == ["a", "b"]


def test_ranking_empty_candidates():
    """Verify handling of empty candidate list."""
    assert rank_candidates("query", []) == []


# ---------------------------------------------------------------------------
# Targeted Conflict Priority Tests (Phase 4 Audit)
# ---------------------------------------------------------------------------

def test_conflicting_priority_prefix_larger_dist_vs_non_prefix_smaller_dist():
    """Audit Test: Demonstrate behavior when a prefix match has LARGER edit distance than a non-prefix match.

    Query: 'comp'
    Candidate A: 'company' -> prefix match (is_prefix=0), edit distance = 3
    Candidate B: 'camp'    -> non-prefix (is_prefix=1), edit distance = 1

    Under the current 5-tier key (is_exact, is_prefix, distance, length_diff, word):
    Tier 2 (is_prefix) evaluates BEFORE Tier 3 (distance).
    Therefore, 'company' (distance 3) ranks BEFORE 'camp' (distance 1).
    """
    query = "comp"
    cand_prefix_high_dist = RankedCandidate("company", 3)
    cand_non_prefix_low_dist = RankedCandidate("camp", 1)

    ranked = rank_candidates(query, [cand_non_prefix_low_dist, cand_prefix_high_dist])

    # Current policy: Prefix match (Tier 2) wins over smaller edit distance (Tier 3)
    assert ranked[0].word == "company"
    assert ranked[0].distance == 3
    assert ranked[1].word == "camp"
    assert ranked[1].distance == 1


def test_conflict_between_multiple_prefix_matches():
    """Audit Test: When multiple candidates both match the prefix, smaller edit distance breaks the tie."""
    query = "comp"
    # Both are prefix matches (is_prefix = 0):
    cand_short = RankedCandidate("compx", 1)      # dist 1
    cand_long = RankedCandidate("computer", 4)    # dist 4
    cand_med = RankedCandidate("company", 3)      # dist 3

    ranked = rank_candidates(query, [cand_long, cand_short, cand_med])

    assert [c.word for c in ranked] == ["compx", "company", "computer"]

