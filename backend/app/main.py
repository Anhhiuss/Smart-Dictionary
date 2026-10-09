"""FastAPI application entry point with lifespan Trie hydration and REST endpoints."""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.api import api_router
from backend.app.core.trie.trie_index import get_trie_index, hydrate_trie_from_db
from backend.app.database.database import SessionLocal, init_db
from backend.app.database.seed import seed_dictionary
from backend.app.repositories.word_repository import WordRepository

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("smart_dictionary")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan context manager: handles startup and shutdown."""
    logger.info("[Startup] Initializing SQLite database...")
    init_db()

    db = SessionLocal()
    try:
        repo = WordRepository(db)
        word_count = repo.count()

        # If database is empty, seed from data/dictionary.json
        if word_count == 0:
            logger.info("[Startup] Database empty. Seeding initial dictionary...")
            imported, _, _ = seed_dictionary(db=db)
            logger.info(f"[Startup] Seed complete: {imported} words imported.")

        # Hydrate in-memory Trie index
        trie = get_trie_index()
        indexed_count = hydrate_trie_from_db(db, trie)
        logger.info(f"[Startup] Trie index successfully hydrated with {indexed_count:,} words.")
    except Exception as e:
        logger.error(f"[Startup Error] Failed during database/Trie startup: {e}")
    finally:
        db.close()

    yield

    logger.info("[Shutdown] Cleaning up resources...")


app = FastAPI(
    title="Smart Dictionary API",
    description=(
        "Dictionary Management System with In-Memory Trie Prefix Search, "
        "Dynamic Programming Levenshtein Distance, and Approximate Fuzzy Matching."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS configuration for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health", tags=["Health"], summary="Health check and index status")
def health_check():
    """Returns application health status, database connectivity, and Trie index size."""
    db = SessionLocal()
    try:
        repo = WordRepository(db)
        db_count = repo.count()
        db_status = "connected"
    except Exception as e:
        db_count = -1
        db_status = f"error: {e}"
    finally:
        db.close()

    trie = get_trie_index()
    return {
        "status": "healthy",
        "database": db_status,
        "trie_indexed_words": trie.size,
        "total_db_words": db_count,
    }


# Include all REST API routes under /api
app.include_router(api_router)
