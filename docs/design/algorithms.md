# Algorithms Specification: Levenshtein Distance, Fuzzy Search & Ranking

## 1. Manual Levenshtein Distance (Dynamic Programming)

### Academic Problem Formulation
Given two strings:
- $S_1$ of length $M$
- $S_2$ of length $N$

The Levenshtein distance is defined as the minimum number of single-character operations required to transform $S_1$ into $S_2$. The allowed edit operations have uniform unit cost ($= 1$):
1. **Insertion**: Insert a single character into $S_1$ (cost = 1).
2. **Deletion**: Delete a single character from $S_1$ (cost = 1).
3. **Substitution**: Replace a single character in $S_1$ with a character from $S_2$ (cost = 1 if different, 0 if identical).

---

### Dynamic Programming Recurrence Relation

Let $D[i][j]$ be the edit distance between prefix $S_1[0 \dots i-1]$ and prefix $S_2[0 \dots j-1]$.

#### Base Cases
$$
\begin{aligned}
D[i][0] &= i \quad \forall \, 0 \le i \le M \quad \text{(deleting all } i \text{ characters from } S_1 \text{ to match } \varepsilon\text{)} \\
D[0][j] &= j \quad \forall \, 0 \le j \le N \quad \text{(inserting all } j \text{ characters to match } S_2\text{)}
\end{aligned}
$$

#### Recurrence Formula
For $1 \le i \le M$ and $1 \le j \le N$:

$$
D[i][j] = \min \begin{cases}
D[i-1][j] + 1 & \text{(Deletion of } S_1[i-1]\text{)} \\
D[i][j-1] + 1 & \text{(Insertion of } S_2[j-1]\text{)} \\
D[i-1][j-1] + \text{cost} & \text{(Substitution, where } \text{cost} = 0 \text{ if } S_1[i-1] = S_2[j-1] \text{ else } 1\text{)}
\end{cases}
$$

#### Proof of Correctness
The problem exhibits optimal substructure. To find the optimal alignment between prefixes $S_1[0 \dots i-1]$ and $S_2[0 \dots j-1]$, the last operation must be either:
- Deleting $S_1[i-1]$, yielding the optimal sub-solution $D[i-1][j] + 1$.
- Inserting $S_2[j-1]$, yielding $D[i][j-1] + 1$.
- Matching or substituting $S_1[i-1]$ with $S_2[j-1]$, yielding $D[i-1][j-1] + \text{cost}$.
Because these three operations exhaust all possibilities for the final character alignment, taking the minimum across all three guarantees the global minimum edit distance.

---

### Complexity Analysis

- **Time Complexity**: $\Theta(M \times N)$
  Each cell in the $(M+1) \times (N+1)$ table requires $O(1)$ operations (one comparison and finding the minimum of three values).
- **Space Complexity**:
  - **Full Matrix (`levenshtein_matrix`)**: $\Theta(M \times N)$ auxiliary space. Preserved for inspection, matrix visualization in documentation, and academic presentation defense.
  - **Two-Row Space-Optimized (`levenshtein_distance`)**: $O(\min(M, N))$ auxiliary space. Since computing $D[i][j]$ requires only row $i-1$ and row $i$, we allocate two rows corresponding to the shorter string.

---

## 2. Fuzzy Search & Candidate Filtering Strategy

Evaluating Levenshtein distance against every word in a large vocabulary $V$ ($O(|V| \cdot M \cdot N)$) would create latency spikes. The system employs **Candidate Filtering by Length Disparity**:

```
User Query (e.g., "comptuer")
      │
      ▼
1. Query Normalization (lowercase, whitespace trimmed)
      │
      ▼
2. Candidate Filtering
   Condition: abs(len(W) - len(Q)) <= max_distance
   (Words failing this bound are pruned BEFORE computing DP)
      │
      ▼
3. Levenshtein Dynamic Programming Calculation
   Compute DP distance for each surviving candidate word W against Q
      │
      ▼
4. Distance Thresholding
   Keep only words where distance <= max_distance (default max_distance = 2)
      │
      ▼
5. Multi-Tier Explainable Ranking
   Sort surviving candidates deterministically
      │
      ▼
6. Top N Extraction
   Return top N results (default limit = 5)
```

### Mathematical Justification for Length Filtering
**Theorem**: Let $W$ and $Q$ be two strings. Then $\text{Levenshtein}(W, Q) \ge | \operatorname{len}(W) - \operatorname{len}(Q) |$.  
**Proof**: Each insertion increases string length by at most 1, each deletion decreases length by at most 1, and substitutions leave length unchanged. Therefore, to reconcile a length difference of $\Delta = | \operatorname{len}(W) - \operatorname{len}(Q) |$, at least $\Delta$ insertion or deletion operations are strictly required. Consequently, if $| \operatorname{len}(W) - \operatorname{len}(Q) | > \text{max\_distance}$, then $\text{Levenshtein}(W, Q) > \text{max\_distance}$ is mathematically guaranteed. Filtering by length before running DP avoids unnecessary $O(M \times N)$ matrix evaluations.

---

## 3. Explainable Multi-Tier Ranking Engine

Results are ordered using an explicit, deterministic 5-tier comparison tuple:

$$\text{Key}(W, Q) = (\text{is\_exact}, \text{is\_prefix}, \text{distance}, \text{length\_diff}, W)$$

### Criteria Hierarchy
1. **Tier 1 — Exact Match (`is_exact`)**:
   $\text{distance} == 0$ yields `0`, all other candidates yield `1`. Exact matches unconditionally rank first.
2. **Tier 2 — Prefix Match Advantage (`is_prefix`)**:
   If candidate $W$ starts with query $Q$, it yields `0`, else `1`. A user intending to type a longer word is prioritized over an accidental mid-word edit.
3. **Tier 3 — Minimal Edit Distance (`distance`)**:
   Lower edit distance precedes higher distance ($1$ before $2$ before $3$).
4. **Tier 4 — Length Proximity (`length_diff`)**:
   $| \operatorname{len}(W) - \operatorname{len}(Q) |$ acts as a tie-breaker. Words with length closer to the query are prioritized when edit distances are tied.
5. **Tier 5 — Deterministic Lexicographical Order ($W$)**:
   Standard alphabetical order ensures reproducible, stable output across multiple runs and environments.
