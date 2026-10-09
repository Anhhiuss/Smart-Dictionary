# Smart Dictionary Dataset (`data/`)

## 1. Overview
The initial lexical dataset (`dictionary.json`) contains **2,218** curated English-Vietnamese vocabulary entries, focused on high-frequency everyday vocabulary, academic terminology, and computer science data structures concepts.

## 2. Data Provenance & Methodology
- **Headwords**: Curated high-frequency English words filtered from the standard Google 10,000 English corpus and foundational Computer Science / DSA vocabulary (e.g., `algorithm`, `binary`, `tree`, `trie`, `stack`, `queue`).
- **Meanings & Parts of Speech**: Extracted from open lexical sources (`data.EV`) with verified Vietnamese definitions and part-of-speech mappings (`noun`, `verb`, `adjective`, `adverb`, `preposition`, `conjunction`, `pronoun`).
- **Pronunciations**: Mapped to standard International Phonetic Alphabet (IPA) transcriptions. Where no phonetic transcription is available in the IPA repository, the field is explicitly stored as `null` rather than generating fabricated phonetic symbols.
- **Usage Examples**: Contextual academic examples demonstrating the headword in active usage.

## 3. Entry Schema
Each entry adheres strictly to the `Word` data model:

```json
{
  "word": "algorithm",
  "meaning": "thuật toán",
  "pronunciation": "/ˈæl.ɡə.rɪ.ðəm/",
  "word_type": "noun",
  "example": "An algorithm is a step-by-step procedure for solving a computational problem."
}
```

## 4. Import & Seeding Instructions
- To import this dataset into the SQLite database, run:
  ```bash
  python scripts/import_dictionary.py
  ```
- To programmatic seed during testing:
  ```python
  from backend.app.database.seed import seed_dictionary
  seed_dictionary()
  ```
