"""Suggestions API routes."""

from typing import Optional
from fastapi import APIRouter, Query, HTTPException
from backend.app.schemas.word import SuggestionsResponse
from backend.app.services.suggestion_service import SuggestionService

router = APIRouter(tags=["Suggestions"])


@router.get(
    "/suggestions",
    response_model=SuggestionsResponse,
    summary="Prefix autocomplete suggestions",
)
def get_suggestions(
    prefix: Optional[str] = Query(None, description="Prefix string to autocomplete"),
    q: Optional[str] = Query(None, description="Alias for prefix query parameter"),
    limit: int = Query(10, ge=1, le=100, description="Maximum suggestions count"),
) -> SuggestionsResponse:
    """Retrieves real-time autocomplete suggestions from in-memory Trie."""
    query_prefix = prefix if prefix is not None else q
    if query_prefix is None or not query_prefix.strip():
        return SuggestionsResponse(prefix="", count=0, suggestions=[])

    service = SuggestionService()
    return service.get_suggestions(prefix=query_prefix, limit=limit)
