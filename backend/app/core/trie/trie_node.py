"""TrieNode representation for in-memory prefix tree."""

from typing import Dict, Optional


class TrieNode:
    """Represents a single node in the Trie structure.

    Attributes:
        children: Mapping from a single character string to its corresponding child TrieNode.
        is_end: Boolean flag indicating if this node marks the termination of a complete word.
        word_id: Foreign key / ID reference to the persistent record in SQLite.
    """

    __slots__ = ("children", "is_end", "word_id")

    def __init__(self) -> None:
        self.children: Dict[str, "TrieNode"] = {}
        self.is_end: bool = False
        self.word_id: Optional[int] = None

    def has_children(self) -> bool:
        """Returns True if this node has at least one child."""
        return bool(self.children)

    def is_leaf(self) -> bool:
        """A leaf node in a Trie has no children."""
        return len(self.children) == 0

    def __repr__(self) -> str:
        return f"<TrieNode(is_end={self.is_end}, word_id={self.word_id}, num_children={len(self.children)})>"
