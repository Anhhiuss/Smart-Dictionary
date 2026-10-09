"""Unit and integration tests for Vietnamese-to-English bidirectional search and autocomplete."""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.fuzzy.levenshtein import (
    has_vietnamese_diacritics,
    strip_vietnamese_diacritics,
)
from backend.app.core.vietnamese.tokenizer import extract_vietnamese_phrases


@pytest.fixture(scope="module")
def client():
    """Module-scoped TestClient that triggers lifespan startup/shutdown."""
    with TestClient(app) as test_client:
        yield test_client


# ---------------------------------------------------------------------------
# 1. Tokenizer and Diacritic Helper Tests
# ---------------------------------------------------------------------------

def test_extract_vietnamese_phrases():
    """Verify tokenizer extracts clean phrases and strips domain annotations."""
    meaning = "(toán học) máy tính; máy vi tính, máy điện toán\nbộ xử lý"
    phrases = extract_vietnamese_phrases(meaning)
    assert "máy tính" in phrases
    assert "máy vi tính" in phrases
    assert "máy điện toán" in phrases
    assert "bộ xử lý" in phrases
    assert all("(" not in p for p in phrases)


def test_strip_vietnamese_diacritics():
    """Verify conversion of accented Vietnamese characters to unaccented form."""
    assert strip_vietnamese_diacritics("máy tính") == "may tinh"
    assert strip_vietnamese_diacritics("điện thoại") == "dien thoai"
    assert strip_vietnamese_diacritics("ĐỒNG HỒ") == "dong ho"
    assert strip_vietnamese_diacritics("computer") == "computer"


def test_has_vietnamese_diacritics():
    """Verify identification of strings containing Vietnamese tone marks."""
    assert has_vietnamese_diacritics("máy tính") is True
    assert has_vietnamese_diacritics("điện thoại") is True
    assert has_vietnamese_diacritics("may tinh") is False
    assert has_vietnamese_diacritics("computer") is False


# ---------------------------------------------------------------------------
# 2. Vietnamese Exact and Unaccented Search via API
# ---------------------------------------------------------------------------

def test_vietnamese_exact_search_may_tinh(client: TestClient):
    """GET /api/search?q=máy tính returns matching English entries."""
    response = client.get("/api/search?q=máy tính")
    assert response.status_code == 200
    data = response.json()
    assert data["match_type"] == "exact"
    assert data["data"] is not None
    assert data["data"]["word"] in ["calculator", "computer", "comptometer"]
    assert "máy tính" in data["data"]["meaning"]


def test_vietnamese_unaccented_search_may_tinh(client: TestClient):
    """GET /api/search?q=may tinh matches accented phrases via inverted unaccented mapping."""
    response = client.get("/api/search?q=may tinh")
    assert response.status_code == 200
    data = response.json()
    assert data["match_type"] == "exact"
    assert data["data"] is not None
    assert data["data"]["word"] in ["calculator", "computer", "comptometer"]


def test_vietnamese_uppercase_search(client: TestClient):
    """GET /api/search?q=MÁY TÍNH normalizes properly and returns exact match."""
    response = client.get("/api/search?q=MÁY TÍNH")
    assert response.status_code == 200
    data = response.json()
    assert data["match_type"] == "exact"
    assert data["data"]["word"] in ["calculator", "computer", "comptometer"]


def test_vietnamese_search_dien_thoai(client: TestClient):
    """Verify both accented 'điện thoại' and unaccented 'dien thoai' find telephone/phone."""
    res_acc = client.get("/api/search?q=điện thoại")
    assert res_acc.status_code == 200
    data_acc = res_acc.json()
    assert data_acc["match_type"] == "exact"
    assert data_acc["data"]["word"] in ["telephone", "phone"]

    res_unacc = client.get("/api/search?q=dien thoai")
    assert res_unacc.status_code == 200
    data_unacc = res_unacc.json()
    assert data_unacc["match_type"] == "exact"
    assert data_unacc["data"]["word"] in ["telephone", "phone"]


# ---------------------------------------------------------------------------
# 3. Vietnamese Prefix Autocomplete via Trie
# ---------------------------------------------------------------------------

def test_vietnamese_prefix_suggestions(client: TestClient):
    """GET /api/suggestions?prefix=máy returns suggestions from Vietnamese Trie."""
    response = client.get("/api/suggestions?prefix=máy&limit=5")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] > 0
    assert any(s.startswith("máy") for s in data["suggestions"])


def test_vietnamese_prefix_search_via_unified_endpoint(client: TestClient):
    """GET /api/search?q=máy t returns match_type='prefix' and candidate English words."""
    response = client.get("/api/search?q=máy t&limit=5")
    assert response.status_code == 200
    data = response.json()
    assert data["match_type"] == "prefix"
    assert len(data["suggestions"]) > 0
    assert len(data["fuzzy_candidates"]) > 0


# ---------------------------------------------------------------------------
# 4. Vietnamese Approximate Fuzzy Search (Typo Recovery via Levenshtein DP)
# ---------------------------------------------------------------------------

def test_vietnamese_fuzzy_search_typo_recovery(client: TestClient):
    """Misspelled Vietnamese query 'máy tin' recovers candidate words via Levenshtein DP."""
    response = client.get("/api/search?q=máy tin&limit=5")
    assert response.status_code == 200
    data = response.json()
    assert data["match_type"] == "fuzzy"
    assert len(data["fuzzy_candidates"]) > 0
    assert any(c["distance"] <= 2 for c in data["fuzzy_candidates"])


# ---------------------------------------------------------------------------
# 5. CRUD Synchronization for Vietnamese Index
# ---------------------------------------------------------------------------

def test_vietnamese_crud_index_synchronization(client: TestClient):
    """Creating a new word with custom Vietnamese meaning immediately allows Vietnamese search."""
    custom_word = {
        "word": "smartlexiword",
        "meaning": "thiết bị học tập thông minh; trí tuệ nhân tạo lexi",
        "pronunciation": "/smɑːt/",
        "word_type": "noun",
        "example": "Testing Vietnamese indexing."
    }
    create_res = client.post("/api/words", json=custom_word)
    assert create_res.status_code == 201
    word_id = create_res.json()["id"]

    try:
        # Search via newly indexed Vietnamese phrase
        search_res = client.get("/api/search?q=thiết bị học tập thông minh")
        assert search_res.status_code == 200
        assert search_res.json()["match_type"] == "exact"
        assert search_res.json()["data"]["word"] == "smartlexiword"

        # Search via unaccented version
        unacc_res = client.get("/api/search?q=thiet bi hoc tap thong minh")
        assert unacc_res.status_code == 200
        assert unacc_res.json()["match_type"] == "exact"
        assert unacc_res.json()["data"]["word"] == "smartlexiword"

        # Trie suggestions for new Vietnamese prefix
        sugg_res = client.get("/api/suggestions?prefix=thiết bị học")
        assert sugg_res.status_code == 200
        assert "thiết bị học tập thông minh" in sugg_res.json()["suggestions"]
    finally:
        client.delete(f"/api/words/{word_id}")

    # Verify pruned from Vietnamese index after deletion
    after_del = client.get("/api/search?q=thiết bị học tập thông minh")
    assert after_del.json()["match_type"] == "none"
