"""Fuzzy approximate search engine using candidate filtering and Levenshtein distance."""

from typing import Any, Iterable, List, Optional, Tuple, Union
from backend.app.core.fuzzy.levenshtein import levenshtein_distance, normalize_string
from backend.app.core.fuzzy.ranking import RankedCandidate, rank_candidates


def fuzzy_search(
    query: str,
    vocabulary: Iterable[Union[str, Tuple[str, Any]]],
    max_distance: int = 2,
    limit: int = 5,
) -> List[RankedCandidate]:
    """Performs approximate fuzzy matching for misspelled queries against a vocabulary.

    Algorithm Workflow:
        1. Normalization: Query string is trimmed and converted to canonical lowercase.
        2. Candidate Filtering: Words are pre-filtered by string length disparity.
           Property: abs(len(W) - len(Q)) <= max_distance.
           Any word violating this condition is mathematically guaranteed to have
           an edit distance exceeding max_distance, avoiding wasteful DP computations.
        3. Dynamic Programming Distance: Compute Levenshtein distance for surviving words.
        4. Distance Thresholding: Keep only words where distance <= max_distance.
        5. Deterministic Ranking: Order results by exact match, prefix advantage, distance,
           length proximity, and alphabetical tie-breaking.
        6. Top N Extraction: Return the top `limit` results.

    Args:
        query: User input query (e.g., "comptuer").
        vocabulary: Iterable of dictionary words, or tuples of (word, payload).
        max_distance: Maximum allowable edit operations (default 2).
        limit: Maximum number of ranked suggestions to return (default 5).

    Returns:
        List of RankedCandidate instances representing top approximate matches.
    """
    normalized_query = normalize_string(query)
    if not normalized_query or max_distance < 0 or limit <= 0:
        return []

    q_len = len(normalized_query)
    surviving_candidates: List[RankedCandidate] = []
    seen_words: set[str] = set()

    for item in vocabulary:
        # Extract word and optional metadata payload
        if isinstance(item, tuple):
            raw_word, payload = item[0], item[1]
        else:
            raw_word, payload = item, None

        word = normalize_string(raw_word)
        if not word or word in seen_words:
            continue

        seen_words.add(word)

        # Stage 1: Candidate Filtering by Length Difference Bound
        # Proof: Transforming W into Q requires at least |len(W) - len(Q)| insertions or deletions.
        if abs(len(word) - q_len) > max_distance:
            continue

        # Stage 2: Calculate Exact Levenshtein Distance via DP
        dist = levenshtein_distance(normalized_query, word, normalize=False)

        # Stage 3: Distance Threshold Check
        if dist <= max_distance:
            surviving_candidates.append(
                RankedCandidate(word=word, distance=dist, payload=payload)
            )

    # Stage 4 & 5: Multi-tier Deterministic Ranking and Top-N Slicing
    return rank_candidates(normalized_query, surviving_candidates, limit=limit)
