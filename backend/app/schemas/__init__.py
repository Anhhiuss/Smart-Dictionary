"""Schemas package."""
from backend.app.schemas.word import (
    WordBase,
    WordCreate,
    WordUpdate,
    WordResponse,
    FuzzyMatchCandidate,
    SearchResult,
    FuzzySearchResult,
    SuggestionsResponse,
    WordListResponse,
)

__all__ = [
    "WordBase",
    "WordCreate",
    "WordUpdate",
    "WordResponse",
    "FuzzyMatchCandidate",
    "SearchResult",
    "FuzzySearchResult",
    "SuggestionsResponse",
    "WordListResponse",
]
