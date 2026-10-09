"""Fuzzy search and Levenshtein algorithms package."""

from backend.app.core.fuzzy.levenshtein import (
    levenshtein_distance,
    levenshtein_matrix,
    normalize_string,
)
from backend.app.core.fuzzy.ranking import (
    RankedCandidate,
    compute_ranking_key,
    rank_candidates,
)
from backend.app.core.fuzzy.fuzzy_search import fuzzy_search

__all__ = [
    "levenshtein_distance",
    "levenshtein_matrix",
    "normalize_string",
    "RankedCandidate",
    "compute_ranking_key",
    "rank_candidates",
    "fuzzy_search",
]
