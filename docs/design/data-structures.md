# Data Structures Specification: In-Memory Trie (Prefix Tree)

## 1. Problem Formulation & Theoretical Justification

In a dictionary application, the most performance-sensitive operation is real-time word suggestion (autocomplete). As a user types each keystroke, the system must retrieve all dictionary entries matching a given prefix $P$.

### Comparison of Alternative Data Structures

| Data Structure | Exact Search Time | Prefix Matching Time | Autocomplete Suggestions Time | Space Complexity | Appropriateness for Prefix Autocomplete |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Unsorted Array / List** | $O(N \cdot L)$ | $O(N \cdot L)$ | $O(N \cdot L)$ | $O(N \cdot L)$ | **Unsuitable**: Requires a full linear scan of all $N$ words on every keystroke. |
| **Sorted Array + Binary Search** | $O(L \log N)$ | $O(L \log N)$ | $O(L \log N + K)$ | $O(N \cdot L)$ | **Sub-optimal**: While range boundaries can be found in $O(L \log N)$, inserting or deleting words dynamically requires $O(N)$ array shifts. |
| **Hash Table** | $O(L)$ average | $O(N)$ | $O(N)$ | $O(N \cdot L)$ | **Unsuitable**: Hash functions destroy key ordering. Finding words starting with prefix $P$ requires scanning every hash bucket ($O(N)$). |
| **Trie (Prefix Tree)** | $O(L)$ | $O(P)$ | $O(P + K)$ | $O(\sum L_i)$ shared | **Optimal**: Directly exploits character-level shared prefixes. Search time depends strictly on the prefix length $P$ and the number of returned suggestions $K$, independent of total dictionary size $N$. |

---

## 2. TrieNode Structure

Defined in `backend/app/core/trie/trie_node.py`:

```python
class TrieNode:
    __slots__ = ("children", "is_end", "word_id")

    def __init__(self) -> None:
        self.children: dict[str, TrieNode] = {}
        self.is_end: bool = False
        self.word_id: int | None = None
```

### Attributes:
- **`children`**: A mapping from a character to the next `TrieNode`. Using a hash map per node allows memory allocation strictly on-demand for existing branch characters.
- **`is_end`**: A boolean flag indicating whether the sequence of characters from the root to this node constitutes a valid, terminal dictionary word.
- **`word_id`**: An integer referencing the primary key `id` of the word in SQLite persistent storage.

---

## 3. Trie Core Operations & Algorithms

Defined in `backend/app/core/trie/trie.py`.

### 3.1. Insert (`insert(word, word_id)`)
- **Algorithm**:
  1. Normalize input: strip whitespace and convert to lowercase.
  2. Starting at `root`, for each character $c$ in the word:
     - If $c$ does not exist in `current.children`, allocate a new `TrieNode`.
     - Advance `current = current.children[c]`.
  3. At the final node, set `is_end = True` and `word_id = word_id`. Increment Trie size if newly added.
- **Time Complexity**: $O(L)$, where $L$ is the length of the word.
- **Space Complexity**: $O(L)$ worst case (when all characters are new); $O(1)$ auxiliary space when shared prefixes exist.

### 3.2. Exact Search (`search(word)`)
- **Algorithm**:
  1. Normalize query word.
  2. Starting at `root`, iteratively follow edges corresponding to each character.
  3. If an edge is missing, return `(False, None)`.
  4. At the final node, return `(True, word_id)` if `is_end == True`, else `(False, None)`.
- **Time Complexity**: $O(L)$, where $L$ is the length of the word.
- **Space Complexity**: $O(1)$ auxiliary space.

### 3.3. Prefix Check (`starts_with(prefix)`)
- **Algorithm**:
  1. Normalize query prefix.
  2. Follow character edges from `root`.
  3. If all characters exist, return `True`. If any character transition is missing, return `False`.
- **Time Complexity**: $O(P)$, where $P$ is the length of the prefix.
- **Space Complexity**: $O(1)$ auxiliary space.

### 3.4. Autocomplete Suggestions (`get_suggestions(prefix, limit)`)
- **Algorithm**:
  1. Normalize query prefix.
  2. **Phase 1 (Prefix Navigation)**: Walk down from `root` using characters in `prefix`. If the prefix path does not exist, return `[]`.
  3. **Phase 2 (Subtree Exploration via Bounded DFS)**:
     - Perform a Depth-First Search starting at the prefix node.
     - Explore child branches in sorted alphabetical order (`sorted(node.children.keys())`) to ensure deterministic output.
     - If `node.is_end` is true, add the reconstructed word to the suggestions list.
     - Stop immediately once `len(suggestions) == limit`.
- **Detailed Complexity Analysis**:
  - **Prefix Traversal Phase**: $O(P)$, where $P$ is the prefix length (steps down the tree from the root).
  - **Child Ordering & Sorting Cost**: At each visited node $v$, sorting its immediate outgoing character edges takes $O(b_v \log b_v)$, where $b_v = |\text{children}(v)| \le |\Sigma|$. Because the alphabet size $|\Sigma|$ is bounded (e.g., $|\Sigma| \le 26$ for English alphabet, or at most a small constant for ASCII), $b_v \log b_v \le |\Sigma| \log |\Sigma| = O(1)$ per node.
  - **Subtree Exploration Phase**: Bounded DFS visits $K$ nodes, where $K$ represents the total number of trie nodes explored before either finding `limit` terminal words or exhausting the subtree. In the best case, $K = O(\text{limit} \cdot \Delta L)$; in the worst case (sparse tree with deep non-terminal paths), $K$ is bounded by the total size of the prefix subtree.
  - **Total Time Complexity**: 
    $$O(P + \sum_{v \in \text{Explored}} b_v \log b_v) = O(P + K \cdot |\Sigma| \log |\Sigma|)$$
    Since $|\Sigma|$ is a fixed constant, this reduces practically to $O(P + K)$, but requires qualification that $K$ is the number of explored nodes (not merely `limit`) and accounts for edge sorting overhead.
  - **Auxiliary Space Complexity**: $O(H)$ recursion stack space, where $H$ is the maximum depth of the explored prefix subtree ($H \le \text{max\_word\_length}$), plus $O(\text{limit} \cdot L_{\max})$ to hold the output suggestion strings.

### 3.5. Delete with Bottom-Up Pruning (`delete(word)`)
- **Algorithm**:
  1. Normalize word.
  2. Traverse recursively to the terminal node. If word does not exist, return `False`.
  3. Set `is_end = False`, `word_id = None`, and decrement size.
  4. On recursion unwinding (bottom-up), check each node:
     - If a node is **not** an end of another word (`is_end == False`) and has **zero children** (`len(children) == 0`), delete it from its parent's `children` dictionary.
     - Pruning halts as soon as an ancestor node is either a terminal node or has other surviving branches.
- **Time Complexity**: $O(L)$, where $L$ is word length.
- **Space Complexity**: $O(L)$ recursion stack space.

---

## 4. Overall Space Complexity Analysis

For a dictionary of $N$ words with average length $L_{\text{avg}}$:
- **Worst-case Space**: $O(\sum_{i=1}^{N} L_i)$ (when no words share any common prefix).
- **Practical Space**: Due to prefix sharing in natural languages (e.g., `comput-` in `computer`, `computing`, `computation`, `computational`), common ancestor nodes are reused.
- Memory is optimized using `__slots__` on `TrieNode` to eliminate Python `__dict__` overhead per node instance.
