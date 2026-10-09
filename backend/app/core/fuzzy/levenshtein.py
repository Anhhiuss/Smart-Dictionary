"""Manual implementation of Levenshtein Distance using Dynamic Programming.

Academic Problem Formulation:
    Given two strings S1 and S2 of lengths M and N respectively, the Levenshtein
    distance is the minimum number of single-character edit operations required
    to transform S1 into S2.

Permitted Operations (Unit Cost = 1):
    1. Insertion: Insert a character into the string.
    2. Deletion: Remove a character from the string.
    3. Substitution: Replace one character with another.

Recurrence Relation:
    Let D[i][j] denote the edit distance between prefixes S1[0...i-1] and S2[0...j-1].

    Base Cases:
        D[i][0] = i   for 0 <= i <= M  (deleting all i characters from S1)
        D[0][j] = j   for 0 <= j <= N  (inserting all j characters to match S2)

    Recursive Step:
        For 1 <= i <= M and 1 <= j <= N:
            If S1[i-1] == S2[j-1]:
                cost = 0
            Else:
                cost = 1

            D[i][j] = min(
                D[i-1][j] + 1,        # Deletion from S1
                D[i][j-1] + 1,        # Insertion into S1
                D[i-1][j-1] + cost    # Substitution
            )

Complexity Analysis:
    Time Complexity:  O(M * N) operations to compute matrix cells.
    Space Complexity:
        - Full Matrix:   O(M * N) space (retained for inspection and visual report).
        - Two-Row DP:    O(min(M, N)) space (optimal for runtime search).
"""

import unicodedata
from typing import List, Optional


import re

def normalize_string(text: Optional[str]) -> str:
    """Canonical normalization consistent with Trie storage (trimmed, lowercased, and NFC canonicalized)."""
    if not text:
        return ""
    return unicodedata.normalize("NFC", text.strip().lower())


def strip_vietnamese_diacritics(text: Optional[str]) -> str:
    """Converts Vietnamese accented characters to plain unaccented ASCII equivalents."""
    if not text:
        return ""
    s = re.sub(r"[đĐ]", "d", text)
    nfkd = unicodedata.normalize("NFKD", s)
    without_marks = "".join(c for c in nfkd if not unicodedata.combining(c))
    return unicodedata.normalize("NFC", without_marks).strip().lower()


def has_vietnamese_diacritics(text: Optional[str]) -> bool:
    """Checks whether the string contains Vietnamese diacritical marks."""
    if not text:
        return False
    norm = normalize_string(text)
    stripped = strip_vietnamese_diacritics(norm)
    return norm != stripped


def levenshtein_matrix(s1: str, s2: str, normalize: bool = True) -> List[List[int]]:
    """Computes the complete (M+1) x (N+1) Dynamic Programming table for Levenshtein Distance.

    This function builds the full matrix explicitly for verification, unit testing,
    and academic presentation defense.

    Args:
        s1: First string (source), length M.
        s2: Second string (target), length N.
        normalize: If True, applies lowercase trimming to both strings.

    Returns:
        Full 2D list of shape (M + 1, N + 1) where matrix[M][N] is the edit distance.
    """
    u = normalize_string(s1) if normalize else (s1 or "")
    v = normalize_string(s2) if normalize else (s2 or "")

    m, n = len(u), len(v)

    # Initialize (m + 1) x (n + 1) matrix
    dp: List[List[int]] = [[0] * (n + 1) for _ in range(m + 1)]

    # Base cases: Transforming prefix to empty string
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j

    # Compute cell transitions
    for i in range(1, m + 1):
        char1 = u[i - 1]
        for j in range(1, n + 1):
            char2 = v[j - 1]
            substitution_cost = 0 if char1 == char2 else 1

            deletion = dp[i - 1][j] + 1
            insertion = dp[i][j - 1] + 1
            substitution = dp[i - 1][j - 1] + substitution_cost

            dp[i][j] = min(deletion, insertion, substitution)

    return dp


def levenshtein_distance(s1: str, s2: str, normalize: bool = True) -> int:
    """Computes the Levenshtein Distance using space-optimized O(min(M, N)) DP.

    Args:
        s1: First string.
        s2: Second string.
        normalize: If True, applies canonical whitespace trimming and lowercasing.

    Returns:
        Minimum integer edit distance between s1 and s2.
    """
    u = normalize_string(s1) if normalize else (s1 or "")
    v = normalize_string(s2) if normalize else (s2 or "")

    # Fast-path optimizations
    if u == v:
        return 0
    if not u:
        return len(v)
    if not v:
        return len(u)

    # Ensure v is the shorter string to minimize row allocation: O(min(M, N)) space
    if len(u) < len(v):
        u, v = v, u

    m, n = len(u), len(v)

    # previous_row stores distances for previous character in u
    previous_row: List[int] = list(range(n + 1))
    current_row: List[int] = [0] * (n + 1)

    for i in range(1, m + 1):
        current_row[0] = i
        char1 = u[i - 1]
        for j in range(1, n + 1):
            char2 = v[j - 1]
            substitution_cost = 0 if char1 == char2 else 1

            deletion = previous_row[j] + 1
            insertion = current_row[j - 1] + 1
            substitution = previous_row[j - 1] + substitution_cost

            current_row[j] = min(deletion, insertion, substitution)

        previous_row, current_row = current_row, previous_row

    return previous_row[n]
