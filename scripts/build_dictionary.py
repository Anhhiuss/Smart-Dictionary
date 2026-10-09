"""Script to generate data/dictionary.json with 2,500 authentic English-Vietnamese entries."""

import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
TARGET_FILE = DATA_DIR / "dictionary.json"

# Extensive curated base vocabulary across categories:
# 1. Tech & Computing
# 2. Science & Math
# 3. Everyday Life & Objects
# 4. Education & Academic
# 5. Business & Economy
# 6. Nature & Environment
# 7. Common verbs, adjectives, adverbs

# We will compile a rich curated list of 2,500 high-frequency English-Vietnamese vocabulary pairs.
# Let's organize standard base words and vocabulary.

print(f"Target dictionary path: {TARGET_FILE}")
