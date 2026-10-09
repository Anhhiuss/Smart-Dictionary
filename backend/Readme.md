# Smart Dictionary — Backend Service

FastAPI backend providing persistent dictionary management (SQLite) accelerated by an in-memory Trie index for prefix autocomplete and dynamic-programming Levenshtein distance for fuzzy misspelling correction.

---

## 1. Prerequisites

- Python 3.10+ (tested on Python 3.13)
- pip

---

## 2. Installation

1. Navigate to the project root directory:
   ```bash
   cd "c:\Users\ADMIN\Desktop\Smart Dictionary"
   ```

2. Install backend dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```

---

## 3. Database Initialization & Seeding

The application automatically initializes SQLite tables and seeds the initial 2,218 English-Vietnamese dictionary entries upon startup if the database is empty.

To manually re-seed or verify data import:
```bash
python scripts/import_dictionary.py
```

---

## 4. Running the FastAPI Server

Start the Uvicorn development server:

```bash
uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

Once running:
- **API Base URL**: `http://127.0.0.1:8000`
- **Interactive Swagger Documentation**: `http://127.0.0.1:8000/docs`
- **ReDoc Documentation**: `http://127.0.0.1:8000/redoc`

---

## 5. Available REST Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/health` | System health, database connection, and indexed word count |
| `GET` | `/api/search?q={query}` | Unified search (distinguishes exact, prefix, fuzzy, none) |
| `GET` | `/api/suggestions?prefix={p}&limit={n}` | Fast in-memory Trie prefix autocomplete |
| `GET` | `/api/words` | Paginated list of words (`skip`, `limit`, `search`) |
| `GET` | `/api/words/{word_id}` | Detailed lexical record for a word |
| `POST` | `/api/words` | Add new word (updates SQLite & inserts into Trie) |
| `PUT` | `/api/words/{word_id}` | Update word (updates SQLite & updates Trie index) |
| `DELETE` | `/api/words/{word_id}` | Delete word (removes from SQLite & prunes Trie) |

---

## 6. Running Tests

Run the complete test suite:

```bash
python -m pytest -v backend/tests/
```
