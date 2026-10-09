# API Design Specification

## Base URL
`/api`

---

## 1. Endpoints Overview

| Method | Endpoint | Description | Input Params / Body | Status Codes |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/api/search` | Search word (exact with fuzzy fallback) | Query param `q` (string) | 200, 400 |
| `GET` | `/api/suggestions` | Prefix autocomplete suggestions | Query param `q` (string), `limit` (int, default 10) | 200, 400 |
| `GET` | `/api/search/fuzzy` | Explicit fuzzy search for misspelled word | Query param `q` (string), `max_distance` (int, default 2) | 200, 400 |
| `GET` | `/api/words` | Browse dictionary entries (paginated) | `skip` (int), `limit` (int), `search` (optional str) | 200 |
| `GET` | `/api/words/{word}` | Get complete word details | Path param `word` (string) | 200, 404 |
| `POST` | `/api/words` | Add new word to dictionary | JSON Body (`WordCreateSchema`) | 201, 400, 409 |
| `PUT` | `/api/words/{word}` | Update word entry | Path param `word`, JSON Body (`WordUpdateSchema`) | 200, 400, 404, 409 |
| `DELETE` | `/api/words/{word}` | Delete word entry | Path param `word` (string) | 200, 404 |

---

## 2. Request & Response Payload Examples

### GET `/api/search?q=computer`
```json
{
  "query": "computer",
  "match_type": "exact",
  "data": {
    "id": 1,
    "word": "computer",
    "meaning": "máy tính",
    "pronunciation": "/kəmˈpjuː.tər/",
    "word_type": "noun",
    "example": "I use my computer every day."
  },
  "suggestions": []
}
```

### GET `/api/search?q=comptuer` (Typo with Fuzzy Fallback)
```json
{
  "query": "comptuer",
  "match_type": "fuzzy",
  "data": null,
  "suggestions": [
    {
      "word": "computer",
      "distance": 2,
      "meaning": "máy tính"
    },
    {
      "word": "commuter",
      "distance": 2,
      "meaning": "người đi vé tháng"
    }
  ]
}
```

### GET `/api/suggestions?q=com&limit=5`
```json
{
  "prefix": "com",
  "count": 5,
  "suggestions": [
    "company",
    "compare",
    "complete",
    "computer",
    "communication"
  ]
}
```
