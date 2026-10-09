"""Unified bidirectional search service (English -> Vietnamese and Vietnamese -> English)."""

from typing import Dict, List, Optional, Set, Tuple
from sqlalchemy.orm import Session
from backend.app.core.fuzzy.fuzzy_search import fuzzy_search
from backend.app.core.fuzzy.levenshtein import (
    has_vietnamese_diacritics,
    normalize_string,
    strip_vietnamese_diacritics,
)
from backend.app.core.fuzzy.ranking import RankedCandidate
from backend.app.core.trie.trie import Trie
from backend.app.core.trie.trie_index import (
    get_trie_index,
    get_vi_phrase_to_word_ids,
    get_vi_unaccent_to_accented,
    get_vietnamese_trie_index,
)
from backend.app.core.vietnamese.tokenizer import extract_vietnamese_phrases
from backend.app.repositories.word_repository import WordRepository
from backend.app.schemas.word import (
    FuzzyMatchCandidate,
    FuzzySearchResult,
    SearchResult,
    WordResponse,
)


class SearchService:
    """Service providing unified bidirectional search distinguishing exact, prefix, and fuzzy matches."""

    def __init__(
        self,
        db: Session,
        trie: Optional[Trie] = None,
        vi_trie: Optional[Trie] = None,
    ):
        self.db = db
        self.repo = WordRepository(db)
        self.trie = trie or get_trie_index()
        self.vi_trie = vi_trie or get_vietnamese_trie_index()

    def search(
        self,
        query: str,
        max_distance: int = 2,
        limit: int = 5,
    ) -> SearchResult:
        """Unified bidirectional search pipeline.

        Decision Flow:
            1. Query is normalized. If empty -> match_type: 'none'.
            2. If query contains Vietnamese diacritics -> route to Vietnamese search pipeline.
            3. If query has no diacritics:
               - Attempt English headword search (Exact -> Prefix).
               - If English matches found -> return English results.
               - Check unaccented Vietnamese match (e.g. 'may tinh' -> 'máy tính').
               - If unaccented Vietnamese matches found -> return Vietnamese results.
               - Fuzzy search fallback (English candidates first, then Vietnamese fuzzy).
        """
        normalized_query = normalize_string(query)
        if not normalized_query:
            return SearchResult(
                query=query or "",
                match_type="none",
                data=None,
                suggestions=[],
                fuzzy_candidates=[],
            )

        # -------------------------------------------------------------
        # Path A: Explicit Vietnamese Accented Query (e.g., 'máy tính', 'điện thoại')
        # -------------------------------------------------------------
        if has_vietnamese_diacritics(normalized_query):
            return self._search_vietnamese(
                query=normalized_query,
                is_unaccented=False,
                max_distance=max_distance,
                limit=limit,
            )

        # -------------------------------------------------------------
        # Path B: Unaccented / English Query
        # Step B1: English Exact Lookup (O(L) via English Trie)
        # -------------------------------------------------------------
        exists, word_id = self.trie.search(normalized_query)
        if exists and word_id is not None:
            db_word = self.repo.get_by_id(word_id)
            if db_word:
                return SearchResult(
                    query=normalized_query,
                    match_type="exact",
                    data=WordResponse.model_validate(db_word),
                    suggestions=[],
                    fuzzy_candidates=[],
                )

        # -------------------------------------------------------------
        # Step B2: English Prefix Matching (O(P + K) via English Trie)
        # -------------------------------------------------------------
        prefix_suggestions = self.trie.get_suggestions(normalized_query, limit=limit)
        if prefix_suggestions:
            return SearchResult(
                query=normalized_query,
                match_type="prefix",
                data=None,
                suggestions=prefix_suggestions,
                fuzzy_candidates=[],
            )

        # -------------------------------------------------------------
        # Step B3: Unaccented Vietnamese Match Check (e.g., 'may tinh' -> 'máy tính')
        # -------------------------------------------------------------
        unaccented_map = get_vi_unaccent_to_accented()
        if normalized_query in unaccented_map:
            # Query is a recognized unaccented Vietnamese phrase
            return self._search_vietnamese(
                query=normalized_query,
                is_unaccented=True,
                max_distance=max_distance,
                limit=limit,
            )

        # -------------------------------------------------------------
        # Step B4: English Fuzzy Search Fallback (Levenshtein DP on English headwords)
        # -------------------------------------------------------------
        en_fuzzy = self._fuzzy_search_english(normalized_query, max_distance=max_distance, limit=limit)
        if en_fuzzy.candidates:
            return SearchResult(
                query=normalized_query,
                match_type="fuzzy",
                data=None,
                suggestions=[c.word for c in en_fuzzy.candidates],
                fuzzy_candidates=en_fuzzy.candidates,
            )

        # -------------------------------------------------------------
        # Step B5: Vietnamese Fuzzy Search Fallback (e.g., 'máy tin' -> 'máy tính')
        # -------------------------------------------------------------
        vi_fuzzy = self._fuzzy_search_vietnamese(normalized_query, max_distance=max_distance, limit=limit)
        if vi_fuzzy.candidates:
            return SearchResult(
                query=normalized_query,
                match_type="fuzzy",
                data=None,
                suggestions=[c.word for c in vi_fuzzy.candidates],
                fuzzy_candidates=vi_fuzzy.candidates,
            )

        # -------------------------------------------------------------
        # Step B6: No Match Found
        # -------------------------------------------------------------
        return SearchResult(
            query=normalized_query,
            match_type="none",
            data=None,
            suggestions=[],
            fuzzy_candidates=[],
        )

    def _search_vietnamese(
        self,
        query: str,
        is_unaccented: bool,
        max_distance: int = 2,
        limit: int = 5,
    ) -> SearchResult:
        """Processes Vietnamese queries to find matching English entries."""
        phrase_to_word_ids = get_vi_phrase_to_word_ids()
        unaccented_map = get_vi_unaccent_to_accented()

        target_phrases: Set[str] = set()

        if not is_unaccented:
            if query in phrase_to_word_ids:
                target_phrases.add(query)
        else:
            if query in unaccented_map:
                target_phrases.update(unaccented_map[query])

        # 1. Exact Vietnamese Phrase Match
        if target_phrases:
            matching_word_ids: List[int] = []
            seen_ids: Set[int] = set()
            for phrase in sorted(target_phrases):
                for wid in phrase_to_word_ids.get(phrase, []):
                    if wid not in seen_ids:
                        seen_ids.add(wid)
                        matching_word_ids.append(wid)

            if matching_word_ids:
                primary_word = self.repo.get_by_id(matching_word_ids[0])
                if primary_word:
                    # Collect other matching headwords as suggestions if multiple entries exist
                    other_words: List[str] = []
                    for wid in matching_word_ids[1:limit]:
                        w = self.repo.get_by_id(wid)
                        if w:
                            other_words.append(w.word)

                    return SearchResult(
                        query=query,
                        match_type="exact",
                        data=WordResponse.model_validate(primary_word),
                        suggestions=other_words,
                        fuzzy_candidates=[],
                    )

        # 2. Vietnamese Prefix Match (e.g. 'máy' -> 'máy tính', 'máy bay')
        vi_suggestions = self.vi_trie.get_suggestions(query, limit=limit)
        if vi_suggestions:
            # Map top suggestion phrases to English words as fuzzy candidates for clear inspection
            candidates: List[FuzzyMatchCandidate] = []
            for phrase in vi_suggestions:
                word_ids = phrase_to_word_ids.get(phrase, set())
                for wid in word_ids:
                    w = self.repo.get_by_id(wid)
                    if w and not any(c.word == w.word for c in candidates):
                        candidates.append(
                            FuzzyMatchCandidate(
                                word=w.word,
                                distance=0,
                                meaning=w.meaning,
                                pronunciation=w.pronunciation,
                                word_type=w.word_type,
                            )
                        )
                    if len(candidates) >= limit:
                        break
                if len(candidates) >= limit:
                    break

            return SearchResult(
                query=query,
                match_type="prefix",
                data=None,
                suggestions=vi_suggestions,
                fuzzy_candidates=candidates,
            )

        # 3. Vietnamese Fuzzy Approximate Match (via Levenshtein DP)
        vi_fuzzy = self._fuzzy_search_vietnamese(query, max_distance=max_distance, limit=limit)
        if vi_fuzzy.candidates:
            return SearchResult(
                query=query,
                match_type="fuzzy",
                data=None,
                suggestions=[c.word for c in vi_fuzzy.candidates],
                fuzzy_candidates=vi_fuzzy.candidates,
            )

        return SearchResult(
            query=query,
            match_type="none",
            data=None,
            suggestions=[],
            fuzzy_candidates=[],
        )

    def _fuzzy_search_english(
        self,
        query: str,
        max_distance: int = 2,
        limit: int = 5,
    ) -> FuzzySearchResult:
        """Candidate-filtered Levenshtein DP against English vocabulary."""
        vocab_items = self.repo.get_all_words_for_fuzzy()
        ranked = fuzzy_search(
            query=query,
            vocabulary=vocab_items,
            max_distance=max_distance,
            limit=limit,
        )

        candidates: List[FuzzyMatchCandidate] = []
        for r in ranked:
            payload = r.payload or {}
            candidates.append(
                FuzzyMatchCandidate(
                    word=r.word,
                    distance=r.distance,
                    meaning=payload.get("meaning"),
                    pronunciation=payload.get("pronunciation"),
                    word_type=payload.get("word_type"),
                )
            )
        return FuzzySearchResult(query=query, candidates=candidates)

    def _fuzzy_search_vietnamese(
        self,
        query: str,
        max_distance: int = 2,
        limit: int = 5,
    ) -> FuzzySearchResult:
        """Candidate-filtered Levenshtein DP against Vietnamese meaning phrases."""
        phrase_to_word_ids = get_vi_phrase_to_word_ids()
        # Build vocabulary from indexed phrases
        vocab_items = [(phrase, phrase) for phrase in phrase_to_word_ids.keys()]

        ranked = fuzzy_search(
            query=query,
            vocabulary=vocab_items,
            max_distance=max_distance,
            limit=limit,
        )

        candidates: List[FuzzyMatchCandidate] = []
        seen_words: Set[str] = set()

        for r in ranked:
            matched_phrase = r.word
            dist = r.distance
            wids = phrase_to_word_ids.get(matched_phrase, set())

            for wid in wids:
                w = self.repo.get_by_id(wid)
                if w and w.word not in seen_words:
                    seen_words.add(w.word)
                    candidates.append(
                        FuzzyMatchCandidate(
                            word=w.word,
                            distance=dist,
                            meaning=f"[{matched_phrase}] {w.meaning}",
                            pronunciation=w.pronunciation,
                            word_type=w.word_type,
                        )
                    )
                if len(candidates) >= limit:
                    break
            if len(candidates) >= limit:
                break

        return FuzzySearchResult(query=query, candidates=candidates)

    def fuzzy_search_candidates(
        self,
        query: str,
        max_distance: int = 2,
        limit: int = 5,
    ) -> FuzzySearchResult:
        """Public endpoint handler for explicit fuzzy search."""
        normalized_query = normalize_string(query)
        if not normalized_query or max_distance < 0 or limit <= 0:
            return FuzzySearchResult(query=query or "", candidates=[])

        if has_vietnamese_diacritics(normalized_query):
            return self._fuzzy_search_vietnamese(normalized_query, max_distance=max_distance, limit=limit)

        en_res = self._fuzzy_search_english(normalized_query, max_distance=max_distance, limit=limit)
        if en_res.candidates:
            return en_res
        return self._fuzzy_search_vietnamese(normalized_query, max_distance=max_distance, limit=limit)
