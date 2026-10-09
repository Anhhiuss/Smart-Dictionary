"""Integration tests for FastAPI endpoints, services, and Trie-DB synchronization."""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.trie.trie_index import get_trie_index


@pytest.fixture(scope="module")
def client():
    """Module-scoped TestClient that triggers lifespan startup/shutdown."""
    with TestClient(app) as test_client:
        yield test_client


# ---------------------------------------------------------------------------
# Health and Startup Verification
# ---------------------------------------------------------------------------

def test_health_endpoint(client: TestClient):
    """GET /api/health must report healthy status, DB connectivity, and hydrated Trie."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"
    assert data["trie_indexed_words"] > 0
    assert data["total_db_words"] > 0
    assert data["trie_indexed_words"] == data["total_db_words"]


# ---------------------------------------------------------------------------
# Search Scenarios: Exact, Prefix, Fuzzy, None
# ---------------------------------------------------------------------------

def test_exact_search(client: TestClient):
    """Exact word lookup returns match_type='exact' and full Word data."""
    response = client.get("/api/search?q=computer")
    assert response.status_code == 200
    res = response.json()
    assert res["match_type"] == "exact"
    assert res["data"] is not None
    assert res["data"]["word"] == "computer"
    assert "máy tính" in res["data"]["meaning"]
    assert res["suggestions"] == []


def test_prefix_search_via_unified_endpoint(client: TestClient):
    """Query matching as prefix returns match_type='prefix' and suggestions list."""
    response = client.get("/api/search?q=comput&limit=5")
    assert response.status_code == 200
    res = response.json()
    assert res["match_type"] == "prefix"
    assert res["data"] is None
    assert len(res["suggestions"]) > 0
    # Suggestions must start with 'comput'
    for s in res["suggestions"]:
        assert s.startswith("comput")


def test_suggestions_endpoint(client: TestClient):
    """GET /api/suggestions returns prefix matching words in alphabetical order."""
    response = client.get("/api/suggestions?prefix=algo&limit=5")
    assert response.status_code == 200
    res = response.json()
    assert res["prefix"] == "algo"
    assert res["count"] > 0
    assert "algorithm" in res["suggestions"]


def test_suggestions_endpoint_using_q_alias(client: TestClient):
    """GET /api/suggestions works with 'q' alias as query parameter."""
    response = client.get("/api/suggestions?q=algo&limit=5")
    assert response.status_code == 200
    res = response.json()
    assert res["prefix"] == "algo"
    assert "algorithm" in res["suggestions"]


def test_suggestions_empty_prefix(client: TestClient):
    """Empty prefix query returns safe empty suggestions response."""
    response = client.get("/api/suggestions?prefix=")
    assert response.status_code == 200
    res = response.json()
    assert res["count"] == 0
    assert res["suggestions"] == []


def test_typo_correction_fuzzy_search(client: TestClient):
    """Misspelled query 'comptuer' triggers fuzzy fallback matching 'computer'."""
    response = client.get("/api/search?q=comptuer&max_distance=2&limit=5")
    assert response.status_code == 200
    res = response.json()
    assert res["match_type"] == "fuzzy"
    assert res["data"] is None
    fuzzy_words = [c["word"] for c in res["fuzzy_candidates"]]
    assert "computer" in fuzzy_words

    # Check top candidate edit distance
    top_cand = next(c for c in res["fuzzy_candidates"] if c["word"] == "computer")
    assert top_cand["distance"] == 2
    assert "máy tính" in top_cand["meaning"]


def test_explicit_fuzzy_search_endpoint(client: TestClient):
    """GET /api/search/fuzzy explicitly returns ranked candidates."""
    response = client.get("/api/search/fuzzy?q=comptuer&max_distance=2&limit=5")
    assert response.status_code == 200
    res = response.json()
    assert res["query"] == "comptuer"
    words = [c["word"] for c in res["candidates"]]
    assert "computer" in words


def test_missing_word_beyond_distance_returns_none(client: TestClient):
    """Completely unrelated nonsensical query returns match_type='none'."""
    response = client.get("/api/search?q=xyzqwe789&max_distance=2")
    assert response.status_code == 200
    res = response.json()
    assert res["match_type"] == "none"
    assert res["data"] is None
    assert res["suggestions"] == []
    assert res["fuzzy_candidates"] == []


# ---------------------------------------------------------------------------
# Dictionary Words CRUD & Real-Time Trie Synchronization
# ---------------------------------------------------------------------------

def test_crud_and_trie_synchronization_lifecycle(client: TestClient):
    """Verifies that adding, updating, and deleting words strictly synchronizes Trie."""
    test_word = "qubit"
    test_meaning = "lượng tử bit trong tính toán lượng tử"

    # Step 1: Ensure test word is NOT initially in Trie or DB
    initial_search = client.get(f"/api/search?q={test_word}")
    assert initial_search.json()["match_type"] != "exact"

    # Step 2: Create word via POST /api/words
    create_payload = {
        "word": test_word,
        "meaning": test_meaning,
        "pronunciation": "/ˈkjuː.bɪt/",
        "word_type": "noun",
        "example": "A qubit can exist in a superposition of states.",
    }
    create_res = client.post("/api/words", json=create_payload)
    assert create_res.status_code == 201
    created_data = create_res.json()
    word_id = created_data["id"]
    assert created_data["word"] == test_word

    # Step 3: Exact search must immediately find the word (Trie synchronized on insert!)
    search_after_create = client.get(f"/api/search?q={test_word}")
    assert search_after_create.status_code == 200
    assert search_after_create.json()["match_type"] == "exact"
    assert search_after_create.json()["data"]["id"] == word_id

    # Step 4: Update headword via PUT /api/words/{id}
    renamed_word = "qubitcore"
    update_payload = {
        "word": renamed_word,
        "meaning": test_meaning + " (updated)",
    }
    update_res = client.put(f"/api/words/{word_id}", json=update_payload)
    assert update_res.status_code == 200
    assert update_res.json()["word"] == renamed_word

    # Step 5: Verify old headword was deleted from Trie, new headword was inserted
    search_old = client.get(f"/api/search?q={test_word}")
    assert search_old.json()["match_type"] != "exact"

    search_new = client.get(f"/api/search?q={renamed_word}")
    assert search_new.json()["match_type"] == "exact"
    assert search_new.json()["data"]["id"] == word_id

    # Step 6: Delete word via DELETE /api/words/{id}
    delete_res = client.delete(f"/api/words/{word_id}")
    assert delete_res.status_code == 200

    # Step 7: Verify word was pruned from Trie and DB
    search_after_delete = client.get(f"/api/search?q={renamed_word}")
    assert search_after_delete.json()["match_type"] != "exact"

    get_after_delete = client.get(f"/api/words/{word_id}")
    assert get_after_delete.status_code == 404


def test_create_duplicate_word_returns_409(client: TestClient):
    """Attempting to create an already existing word returns HTTP 409 Conflict."""
    payload = {
        "word": "computer",
        "meaning": "máy vi tính",
        "word_type": "noun",
    }
    response = client.post("/api/words", json=payload)
    assert response.status_code == 409
    assert "already exists" in response.json()["detail"]


def test_update_to_duplicate_word_returns_409(client: TestClient):
    """Attempting to update a word to another existing headword returns 409 Conflict."""
    # Create temporary word
    temp = client.post(
        "/api/words",
        json={"word": "uniquealpha", "meaning": "nghĩa thử nghiệm"},
    ).json()
    temp_id = temp["id"]

    try:
        # Attempt to rename it to 'computer' (which already exists)
        rename_res = client.put(
            f"/api/words/{temp_id}",
            json={"word": "computer"},
        )
        assert rename_res.status_code == 409
        assert "already exists" in rename_res.json()["detail"]
    finally:
        client.delete(f"/api/words/{temp_id}")


def test_get_nonexistent_word_returns_404(client: TestClient):
    """GET /api/words/{invalid_id} returns HTTP 404."""
    response = client.get("/api/words/9999999")
    assert response.status_code == 404


def test_delete_nonexistent_word_returns_404(client: TestClient):
    """DELETE /api/words/{invalid_id} returns HTTP 404."""
    response = client.delete("/api/words/9999999")
    assert response.status_code == 404


def test_invalid_request_data_validation(client: TestClient):
    """POST /api/words with missing meaning or blank word returns 422 Unprocessable Entity."""
    # Blank word
    res1 = client.post("/api/words", json={"word": "   ", "meaning": "hợp lệ"})
    assert res1.status_code == 422

    # Missing meaning
    res2 = client.post("/api/words", json={"word": "validword"})
    assert res2.status_code == 422


def test_list_words_pagination(client: TestClient):
    """GET /api/words supports pagination parameters."""
    response = client.get("/api/words?skip=0&limit=10")
    assert response.status_code == 200
    items = response.json()
    assert isinstance(items, list)
    assert len(items) == 10
