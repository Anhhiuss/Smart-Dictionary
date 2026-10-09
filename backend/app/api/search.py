"""Search API routes."""

from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.app.database.database import get_db
from backend.app.schemas.word import FuzzySearchResult, SearchResult
from backend.app.services.search_service import SearchService

router = APIRouter(tags=["Search"])


@router.get("/search", response_model=SearchResult, summary="Unified dictionary search")
def search_word(
    q: str = Query(..., min_length=1, description="Search query string"),
    max_distance: int = Query(2, ge=0, le=5, description="Maximum edit distance for fuzzy matching"),
    limit: int = Query(5, ge=1, le=50, description="Maximum suggestions or fuzzy candidates"),
    db: Session = Depends(get_db),
) -> SearchResult:
    """Performs unified search.

    Distinguishes:
        - 'exact': The query exactly matches a dictionary headword.
        - 'prefix': The query matches as a prefix to one or more words.
        - 'fuzzy': The query is misspelled; approximate words are found via Levenshtein DP.
        - 'none': No exact, prefix, or approximate match exists.
    """
    service = SearchService(db)
    return service.search(query=q, max_distance=max_distance, limit=limit)


@router.get(
    "/search/fuzzy",
    response_model=FuzzySearchResult,
    summary="Explicit approximate fuzzy search",
)
def fuzzy_search_words(
    q: str = Query(..., min_length=1, description="Misspelled query string"),
    max_distance: int = Query(2, ge=0, le=5, description="Maximum edit distance"),
    limit: int = Query(5, ge=1, le=50, description="Maximum results"),
    db: Session = Depends(get_db),
) -> FuzzySearchResult:
    """Computes approximate matches for a query using Levenshtein distance."""
    service = SearchService(db)
    return service.fuzzy_search_candidates(query=q, max_distance=max_distance, limit=limit)
