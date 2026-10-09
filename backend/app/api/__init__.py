"""API routers package."""

from fastapi import APIRouter
from backend.app.api.search import router as search_router
from backend.app.api.suggestions import router as suggestions_router
from backend.app.api.words import router as words_router

api_router = APIRouter(prefix="/api")
api_router.include_router(search_router)
api_router.include_router(suggestions_router)
api_router.include_router(words_router)

__all__ = ["api_router", "search_router", "suggestions_router", "words_router"]
