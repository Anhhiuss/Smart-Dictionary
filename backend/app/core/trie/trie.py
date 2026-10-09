"""Trie (Prefix Tree) implementation for fast prefix matching and autocomplete."""

from typing import List, Optional, Tuple
from backend.app.core.trie.trie_node import TrieNode


class Trie:
    """In-memory Trie (Prefix Tree) data structure for dictionary lookup.

    Operations:
        - insert(word, word_id): O(L) time, where L is word length.
        - search(word): O(L) time.
        - starts_with(prefix): O(P) time, where P is prefix length.
        - get_suggestions(prefix, limit): O(P + K) time, where K is explored nodes.
        - delete(word): O(L) time with bottom-up node pruning.
    """

    def __init__(self) -> None:
        self.root: TrieNode = TrieNode()
        self._size: int = 0

    @property
    def size(self) -> int:
        """Returns the number of unique words indexed in the Trie."""
        return self._size

    @staticmethod
    def normalize(text: Optional[str]) -> str:
        """Sanitizes and normalizes input to lowercase trimmed format in canonical NFC form."""
        if not text:
            return ""
        import unicodedata
        return unicodedata.normalize("NFC", text.strip().lower())

    def insert(self, word: str, word_id: int) -> bool:
        """Inserts a word and its corresponding database ID into the Trie.

        Args:
            word: The headword string.
            word_id: Integer primary key from SQLite.

        Returns:
            True if word was newly inserted or updated, False if input was invalid/empty.
        """
        normalized = self.normalize(word)
        if not normalized:
            return False

        current = self.root
        for char in normalized:
            if char not in current.children:
                current.children[char] = TrieNode()
            current = current.children[char]

        was_new = not current.is_end
        if was_new:
            self._size += 1

        current.is_end = True
        current.word_id = word_id
        return True

    def search(self, word: str) -> Tuple[bool, Optional[int]]:
        """Searches for an exact word in the Trie.

        Args:
            word: The query word string.

        Returns:
            Tuple of (exists: bool, word_id: Optional[int]).
        """
        normalized = self.normalize(word)
        if not normalized:
            return False, None

        current = self.root
        for char in normalized:
            if char not in current.children:
                return False, None
            current = current.children[char]

        if current.is_end:
            return True, current.word_id
        return False, None

    def starts_with(self, prefix: str) -> bool:
        """Checks if any word in the Trie begins with the specified prefix.

        Args:
            prefix: The prefix string to verify.

        Returns:
            True if at least one word shares this prefix, False otherwise.
        """
        normalized = self.normalize(prefix)
        if not normalized:
            return False

        current = self.root
        for char in normalized:
            if char not in current.children:
                return False
            current = current.children[char]

        return True

    def get_suggestions(self, prefix: str, limit: int = 10) -> List[str]:
        """Collects autocomplete suggestions sharing the given prefix.

        Traversal uses lexicographical ordering of child branches to ensure
        deterministic results.

        Args:
            prefix: The query prefix.
            limit: Maximum number of suggestions to return (default 10).

        Returns:
            List of suggested word strings.
        """
        normalized = self.normalize(prefix)
        if not normalized or limit <= 0:
            return []

        # Step 1: Traverse to prefix node in O(P)
        current = self.root
        for char in normalized:
            if char not in current.children:
                return []
            current = current.children[char]

        # Step 2: Perform bounded DFS from prefix node in O(K)
        suggestions: List[str] = []

        def _dfs(node: TrieNode, path: List[str]) -> None:
            if len(suggestions) >= limit:
                return

            if node.is_end:
                suggestions.append("".join(path))
                if len(suggestions) >= limit:
                    return

            # Deterministic alphabetical child exploration
            for char in sorted(node.children.keys()):
                path.append(char)
                _dfs(node.children[char], path)
                path.pop()
                if len(suggestions) >= limit:
                    return

        _dfs(current, list(normalized))
        return suggestions

    def delete(self, word: str) -> bool:
        """Deletes a word from the Trie and recursively prunes unused nodes.

        Args:
            word: The headword to delete.

        Returns:
            True if the word was found and deleted, False otherwise.
        """
        normalized = self.normalize(word)
        if not normalized:
            return False

        def _delete_helper(node: TrieNode, word_str: str, depth: int) -> Tuple[bool, bool]:
            """Recursive helper for bottom-up deletion and pruning.

            Returns:
                Tuple of (word_deleted: bool, can_prune_node: bool).
            """
            if depth == len(word_str):
                if not node.is_end:
                    return False, False  # Word not marked as end

                node.is_end = False
                node.word_id = None
                self._size -= 1
                # Can prune this node if it has no further children
                return True, (len(node.children) == 0)

            char = word_str[depth]
            if char not in node.children:
                return False, False

            child_node = node.children[char]
            word_deleted, can_prune_child = _delete_helper(child_node, word_str, depth + 1)

            if can_prune_child:
                del node.children[char]

            # Prune this current node if it's not the end of another word and has no remaining children
            can_prune_current = (not node.is_end) and (len(node.children) == 0)
            return word_deleted, can_prune_current

        deleted, _ = _delete_helper(self.root, normalized, 0)
        return deleted

    def clear(self) -> None:
        """Resets the Trie to an empty root state."""
        self.root = TrieNode()
        self._size = 0
