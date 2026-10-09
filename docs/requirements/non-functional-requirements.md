# Non-Functional Requirements Specification (NFRS)

## Project: Smart Dictionary
**Subject:** Data Structures and Algorithms  
**Target:** Performance Targets, Reliability, Maintainability & Academic Rigor  

---

## 1. Measurable Performance Targets & Empirical Benchmarking

> **Methodology Note**: Performance criteria are defined as **measurable empirical targets** to be evaluated under documented hardware/OS specifications. No performance claim is considered validated until measured and recorded via automated benchmark runs.

- **NFR-01 (Prefix Lookup Scaling Target)**:
  - Trie prefix lookup time must be experimentally measured across vocabulary scales ($1\text{K}$, $5\text{K}$, $10\text{K}$, $50\text{K}$, $100\text{K}$).
  - Target behavior: Prefix lookup latency must scale with prefix length $O(P)$ and result set size $O(K)$, remaining substantially flat relative to overall corpus size $N$, contrasting with Linear Search $O(N)$.
- **NFR-02 (Fuzzy Search Latency Target under Candidate Pruning)**:
  - Using length-difference pruning ($||W| - |Q|| \le \text{max\_distance}$), evaluate fuzzy search execution times on the standard dictionary dataset ($2,000 - 5,000$ words).
  - Target: Maintain an interactive response profile suitable for user-initiated typo correction.
- **NFR-03 (Startup Indexing Throughput Target)**:
  - Measure the time required to read words from SQLite and hydrate the in-memory Trie index during application startup.
  - Record throughput in records indexed per second.
- **NFR-04 (Memory Footprint Profile)**:
  - Benchmark the actual RAM consumption of the in-memory Trie against dataset sizes ($1\text{K}$ to $100\text{K}$ words) using process memory profiling tools (`tracemalloc` / `psutil`).

---

## 2. Theoretical Complexity Guarantees

- **NFR-05 (Algorithmic Rigor)**:
  - **Trie Insert**: $O(L)$, where $L$ is word length.
  - **Trie Exact Search**: $O(L)$.
  - **Trie Prefix Traversal**: $O(P + K)$, where $P$ is prefix length and $K$ is total nodes explored within the prefix subtree.
  - **Trie Node Deletion & Pruning**: $O(L)$ with clean deallocation of non-shared descendant nodes.
  - **Levenshtein Distance**: $O(M \times N)$ time using dynamic programming recurrence, where $M$ and $N$ are lengths of the compared words.
  - **Candidate Filtering**: $O(V)$ length-difference check filter followed by Levenshtein distance on surviving candidate subset $C \ll V$.

---

## 3. Reliability, Data Integrity & Synchronization

- **NFR-06 (Persistence as Source of Truth)**:
  - SQLite serves as the persistent source of truth with ACID guarantees.
  - In-memory Trie serves as an accelerated search index.
  - State synchronization lifecycle:
    - *Startup*: SQLite $\rightarrow$ bulk read $\rightarrow$ Trie hydration.
    - *Create*: Database commit $\rightarrow$ `Trie.insert(word, id)`.
    - *Delete*: Database commit $\rightarrow$ `Trie.delete(word)`.
    - *Update*: Database commit $\rightarrow$ `Trie.delete(old_word)` $\rightarrow$ `Trie.insert(new_word, id)`.
- **NFR-07 (Input Validation & Error Tolerance)**:
  - Strict input sanitization (trimming, lowercase normalization).
  - Proper HTTP error codes (400 Bad Request, 404 Not Found, 409 Conflict for duplicate words, 422 Unprocessable Entity).
  - Clean error states in frontend without uncaught exceptions or UI crashes.

---

## 4. Academic Presentation & Usability

- **NFR-08 (Educational Transparency)**:
  - Zero external black-box search/distance libraries (no third-party Trie or Levenshtein packages).
  - Code must remain clean, well-commented, and directly inspectable by university evaluators.
- **NFR-09 (Responsive, Purpose-Driven UI)**:
  - Focused lexicographical interface prioritizing readability, typography, and state feedback (Idle, Loading, Exact Result, "Did you mean?" suggestions, Empty state).
  - No decorative bloat or AI-dashboard widgets.
