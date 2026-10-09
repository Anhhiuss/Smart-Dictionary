"""Words CRUD API routes."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from backend.app.database.database import get_db
from backend.app.schemas.word import WordCreate, WordResponse, WordUpdate
from backend.app.services.dictionary_service import (
    DictionaryService,
    WordAlreadyExistsError,
)

router = APIRouter(prefix="/words", tags=["Words"])


@router.get("", response_model=List[WordResponse], summary="List words with pagination")
def list_words(
    skip: int = Query(0, ge=0, description="Offset for pagination"),
    limit: int = Query(50, ge=1, le=200, description="Page size limit"),
    search: Optional[str] = Query(None, description="Optional substring search filter"),
    db: Session = Depends(get_db),
) -> List[WordResponse]:
    """Retrieves paginated list of words from SQLite."""
    service = DictionaryService(db)
    _, items = service.list_words(skip=skip, limit=limit, search_filter=search)
    return [WordResponse.model_validate(w) for w in items]


@router.get("/{word_id}", response_model=WordResponse, summary="Get word by ID")
def get_word(
    word_id: int,
    db: Session = Depends(get_db),
) -> WordResponse:
    """Retrieves complete details of a word by primary key ID."""
    service = DictionaryService(db)
    word = service.get_by_id(word_id)
    if not word:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Word with ID {word_id} not found",
        )
    return WordResponse.model_validate(word)


@router.post(
    "",
    response_model=WordResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new dictionary word",
)
def create_word(
    word_in: WordCreate,
    db: Session = Depends(get_db),
) -> WordResponse:
    """Creates a new word in SQLite and updates the in-memory Trie index."""
    service = DictionaryService(db)
    try:
        created = service.create_word(word_in)
        return WordResponse.model_validate(created)
    except WordAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )


@router.put("/{word_id}", response_model=WordResponse, summary="Update an existing word")
def update_word(
    word_id: int,
    word_in: WordUpdate,
    db: Session = Depends(get_db),
) -> WordResponse:
    """Updates an existing word and synchronizes the Trie index."""
    service = DictionaryService(db)
    try:
        updated = service.update_word(word_id, word_in)
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Word with ID {word_id} not found",
            )
        return WordResponse.model_validate(updated)
    except WordAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )


@router.delete("/{word_id}", summary="Delete a dictionary word")
def delete_word(
    word_id: int,
    db: Session = Depends(get_db),
):
    """Deletes a word from SQLite and prunes its entry from the Trie index."""
    service = DictionaryService(db)
    deleted = service.delete_word(word_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Word with ID {word_id} not found",
        )
    return {"success": True, "message": f"Word with ID {word_id} successfully deleted"}
