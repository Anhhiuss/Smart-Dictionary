import unicodedata
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator


class WordBase(BaseModel):
    """Base schema for word attributes."""

    word: str = Field(..., min_length=1, max_length=100, description="Dictionary headword")
    meaning: str = Field(..., min_length=1, description="Meaning and definitions")
    pronunciation: Optional[str] = Field(None, max_length=100, description="Phonetic transcription (IPA)")
    word_type: Optional[str] = Field(None, max_length=50, description="Part of speech (e.g. noun, verb)")
    example: Optional[str] = Field(None, description="Contextual usage example")

    @field_validator("word")
    @classmethod
    def normalize_word(cls, v: str) -> str:
        trimmed = unicodedata.normalize("NFC", v.strip().lower())
        if not trimmed:
            raise ValueError("Word cannot be empty or blank")
        return trimmed

    @field_validator("meaning")
    @classmethod
    def validate_meaning(cls, v: str) -> str:
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("Meaning cannot be empty or blank")
        return trimmed


class WordCreate(WordBase):
    """Schema for creating a new word entry."""
    pass


class WordUpdate(BaseModel):
    """Schema for updating an existing word entry."""

    word: Optional[str] = Field(None, min_length=1, max_length=100)
    meaning: Optional[str] = Field(None, min_length=1)
    pronunciation: Optional[str] = Field(None, max_length=100)
    word_type: Optional[str] = Field(None, max_length=50)
    example: Optional[str] = None

    @field_validator("word")
    @classmethod
    def normalize_word(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            trimmed = unicodedata.normalize("NFC", v.strip().lower())
            if not trimmed:
                raise ValueError("Word cannot be empty or blank")
            return trimmed
        return v

    @field_validator("meaning")
    @classmethod
    def validate_meaning(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            trimmed = v.strip()
            if not trimmed:
                raise ValueError("Meaning cannot be empty or blank")
            return trimmed
        return v


class WordResponse(WordBase):
    """Schema for returning word data to clients."""

    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class FuzzyMatchCandidate(BaseModel):
    """Candidate representation in fuzzy approximate search results."""

    word: str
    distance: int
    meaning: Optional[str] = None
    pronunciation: Optional[str] = None
    word_type: Optional[str] = None


class SearchResult(BaseModel):
    """Uniform search response distinguishing exact, prefix, and fuzzy matches."""

    query: str
    match_type: str = Field(..., description="'exact', 'prefix', 'fuzzy', or 'none'")
    data: Optional[WordResponse] = None
    suggestions: List[str] = Field(default_factory=list, description="Prefix suggestions")
    fuzzy_candidates: List[FuzzyMatchCandidate] = Field(
        default_factory=list, description="Ranked approximate matches with edit distances"
    )


class SuggestionsResponse(BaseModel):
    """Autocomplete suggestions response."""

    prefix: str
    count: int
    suggestions: List[str]


class FuzzySearchResult(BaseModel):
    """Fuzzy search response containing ranked candidates and their edit distances."""

    query: str
    candidates: List[FuzzyMatchCandidate] = Field(default_factory=list)


class WordListResponse(BaseModel):
    """Paginated list of words."""

    total: int
    skip: int
    limit: int
    items: List[WordResponse]

