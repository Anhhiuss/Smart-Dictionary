"""Vietnamese meaning phrase tokenizer and inverted indexing helpers."""

import re
from typing import List, Set
from backend.app.core.fuzzy.levenshtein import (
    normalize_string,
    strip_vietnamese_diacritics,
)


def extract_vietnamese_phrases(meaning: str) -> List[str]:
    """Tokenizes and cleans Vietnamese meanings into discrete searchable phrases.

    Vietnamese definitions in bilingual dictionaries typically separate sub-senses
    and phrases with semicolons, commas, slashes, or newlines (e.g., 'máy tính; máy vi tính').
    This function splits by these delimiters, strips extraneous parenthetical domain notes
    (such as '(toán học)'), and normalizes into canonical Unicode NFC lowercase phrases.

    Args:
        meaning: Raw Vietnamese meaning string from dictionary entry.

    Returns:
        List of distinct normalized phrase strings.
    """
    if not meaning:
        return []

    # Split by standard dictionary phrase delimiters: semicolon, comma, newline, slash
    raw_segments = re.split(r"[;,\n/]+", meaning)
    phrases: List[str] = []
    seen: Set[str] = set()

    for seg in raw_segments:
        # Strip domain annotations like (toán học), [kỹ thuật]
        cleaned = re.sub(r"^[(\[{].*?[)\]}]\s*", "", seg.strip())
        cleaned = cleaned.strip(" .;:-()\"'")
        if not cleaned:
            continue

        normalized = normalize_string(cleaned)
        if normalized and normalized not in seen:
            seen.add(normalized)
            phrases.append(normalized)

    return phrases
