# Functional Requirements Specification (FRS)

## Project: Smart Dictionary
**Subject:** Data Structures and Algorithms  
**Target:** Web-based Dictionary Management & Approximate Search System  

---

## 1. Overview
The Smart Dictionary is an academic and practical software project designed to demonstrate the real-world application of foundational Data Structures and Algorithms (DSA). Rather than relying on black-box external search engines, the system implements an in-memory **Trie** for exact and prefix retrieval, coupled with a manual dynamic-programming implementation of **Levenshtein Distance** for fuzzy error tolerance and ranking.

---

## 2. User Roles & Actors

1. **General User (Learner / Searcher)**:
   - Performs exact keyword lookups.
   - Explores suggestions via incremental prefix matching.
   - Searches for misspelled or uncertain words, receiving ranked fuzzy corrections.
   - Views comprehensive lexical details (phonetics, parts of speech, definitions, example sentences).
   - Views search history (session or local storage).

2. **Dictionary Manager (Administrator / Lexicographer)**:
   - Manages the lexical database (CRUD operations: Create, Read, Update, Delete).
   - Ensures data integrity and consistency between persistent storage (SQLite) and runtime search indexes (In-Memory Trie).

---

## 3. Detailed Functional Modules

### FR-01: Input Sanitization & Normalization
- **FR-01.1**: The system must strip all leading and trailing whitespace characters.
- **FR-01.2**: Case normalization: All query strings and indexed headwords must be converted to uniform lowercase (e.g., `" Computer "` → `"computer"`).
- **FR-01.3**: Character validation: Headwords must support alphanumeric characters and standard hyphenation/apostrophes (e.g., `well-being`, `o'clock`), rejecting control characters or non-textual payloads.
- **FR-01.4**: Empty input handling: Empty or whitespace-only queries must not trigger search traversals and should yield an immediate empty state without throwing exceptions.

### FR-02: Exact Word Search
- **FR-02.1**: The system must verify whether a normalized word exists in the Trie in $O(L)$ time, where $L$ is the word length.
- **FR-02.2**: If the word is marked as terminal (`is_end == True`), retrieve the corresponding `word_id` and load the complete dictionary record.
- **FR-02.3**: If the word exists, render full details including definition, phonetic pronunciation, word type, and usage example.

### FR-03: Real-Time Prefix Search & Autocomplete
- **FR-03.1**: As the user types a prefix $P$ into the search bar, the system queries the Trie for auto-suggestions with an exploration limit $K$ (default $K = 5$ or $10$).
- **FR-03.2**: The prefix search must traverse down to the node matching $P$ in $O(|P|)$ time, followed by a bounded Depth-First Search (DFS) / Breadth-First Search (BFS) subtree traversal.
- **FR-03.3**: Suggestions must be returned in sub-10ms response times for responsive debounced UI rendering.

### FR-04: Approximate / Fuzzy Search & Misspelling Recovery
- **FR-04.1**: If an exact match is not found (or if fuzzy search is explicitly queried), the system must compute the edit distance using custom Levenshtein Distance algorithms.
- **FR-04.2**: The algorithm must calculate the minimum edit distance considering insertions, deletions, and substitutions.
- **FR-04.3**: Fuzzy matching should be bounded by a maximum distance threshold (e.g., $\text{max\_distance} = 2$ or $3$, dynamically scaled to word length).
- **FR-04.4**: For query $Q$, each candidate word $W$ must return its computed distance:
  $$\text{dist}(Q, W)$$

### FR-05: Result Ranking
- **FR-05.1**: Candidate suggestions must be ranked deterministically using explicit multi-tier criteria:
  1. **Tier 1 (Exact Match)**: Distance $= 0$ (highest priority).
  2. **Tier 2 (Prefix Match Advantage)**: Candidates sharing the query as a strict prefix receive higher priority.
  3. **Tier 3 (Minimal Edit Distance)**: Smaller Levenshtein distance precedes larger distance.
  4. **Tier 4 (Length Difference / Lexicographical)**: If distances are tied, words with closer length to query and alphabetical tie-breaking are preferred.

### FR-06: Dictionary Management (CRUD)
- **FR-06.1 (Create)**:
  - Add a new word entry with headword, pronunciation, word type (noun, verb, adj, etc.), meaning, and usage example.
  - Persist the record in SQLite.
  - Insert the word into the runtime Trie in-memory index immediately upon successful database commit.
  - Prevent duplicate headword creation with clear HTTP 409 Conflict validation.
- **FR-06.2 (Read / Browse)**:
  - Retrieve paginated list of dictionary entries with search/filter capabilities.
  - Retrieve word detail by ID or exact headword.
- **FR-06.3 (Update)**:
  - Edit existing lexical attributes.
  - If the headword itself is modified: remove the old headword from the Trie and insert the new headword into the Trie.
  - Persist changes to SQLite with automatic `updated_at` timestamp.
- **FR-06.4 (Delete)**:
  - Require explicit user confirmation before deletion.
  - Delete record from SQLite.
  - Evict headword from the Trie structure (pruning orphaned unshared child nodes where appropriate).

### FR-07: Synchronization & Startup Indexing
- **FR-07.1**: Upon backend application startup, the system must warm up the Trie by bulk-reading all valid words from SQLite and inserting them into the Trie.
- **FR-07.2**: In-memory Trie and SQLite database must remain in strict consistency throughout runtime mutations.

### FR-08: Performance Benchmarking
- **FR-08.1**: The system must provide a dedicated benchmark module comparing Linear Search ($O(N)$) against Trie Search ($O(L)$) across standard dataset sizes (1K, 5K, 10K, 50K, 100K entries).
- **FR-08.2**: Metrics measured: Average lookup latency, throughput (lookups/sec), and memory footprint.
