"""Suggestion service handling prefix autocomplete queries via English and Vietnamese Tries."""

from typing import List, Optional, Set
from backend.app.core.fuzzy.levenshtein import (
    has_vietnamese_diacritics,
    strip_vietnamese_diacritics,
)
from backend.app.core.trie.trie import Trie
from backend.app.core.trie.trie_index import (
    get_trie_index,
    get_vi_unaccent_to_accented,
    get_vietnamese_trie_index,
)
from backend.app.schemas.word import SuggestionsResponse


class SuggestionService:
    """Service providing high-speed autocomplete suggestions from in-memory Tries."""

    def __init__(self, en_trie: Optional[Trie] = None, vi_trie: Optional[Trie] = None):
        self.en_trie = en_trie or get_trie_index()
        self.vi_trie = vi_trie or get_vietnamese_trie_index()

    def get_suggestions(self, prefix: str, limit: int = 10) -> SuggestionsResponse:
        """Retrieves deterministic autocomplete suggestions sharing the query prefix.

        Supports both English headwords and Vietnamese meaning phrases:
        1. If prefix contains Vietnamese diacritics -> query Vietnamese Trie directly.
        2. If prefix has no diacritics:
           - First query English Trie.
           - If English suggestions found, return them.
           - If no English suggestions found, check unaccented Vietnamese prefixes.

        Args:
            prefix: Input prefix string (e.g., 'comp' or 'máy').
            limit: Maximum count of suggestions to return.

        Returns:
            SuggestionsResponse containing matching suggestions and count.
        """
        normalized_prefix = self.en_trie.normalize(prefix)
        if not normalized_prefix or limit <= 0:
            return SuggestionsResponse(
                prefix=prefix or "",
                count=0,
                suggestions=[],
            )

        # 1. Accented Vietnamese query
        if has_vietnamese_diacritics(normalized_prefix):
            vi_suggestions = self.vi_trie.get_suggestions(normalized_prefix, limit=limit)
            return SuggestionsResponse(
                prefix=normalized_prefix,
                count=len(vi_suggestions),
                suggestions=vi_suggestions,
            )

        # 2. English query
        en_suggestions = self.en_trie.get_suggestions(normalized_prefix, limit=limit)
        if en_suggestions:
            return SuggestionsResponse(
                prefix=normalized_prefix,
                count=len(en_suggestions),
                suggestions=en_suggestions,
            )

        # 3. Unaccented Vietnamese query fallback (e.g., "may" -> "máy", "máy tính")
        unaccented_map = get_vi_unaccent_to_accented()
        vi_suggestions: List[str] = []
        seen: Set[str] = set()

        # Find unaccented phrases starting with normalized_prefix
        for unacc, accented_set in unaccented_map.items():
            if unacc.startswith(normalized_prefix):
                for acc in sorted(accented_set):
                    if acc not in seen:
                        seen.add(acc)
                        vi_suggestions.append(acc)
                        if len(vi_suggestions) >= limit:
                            break
            if len(vi_suggestions) >= limit:
                break

        return SuggestionsResponse(
            prefix=normalized_prefix,
            count=len(vi_suggestions),
            suggestions=vi_suggestions,
        )
