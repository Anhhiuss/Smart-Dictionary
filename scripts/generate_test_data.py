"""Generate benchmark synthetic vocabulary datasets of varying sizes (1K, 5K, 10K, 50K, 100K)."""

import json
import random
import string
from pathlib import Path
from typing import List, Set

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "benchmarks"


def generate_unique_words(target_count: int, seed: int = 42) -> List[str]:
    """Generates target_count unique realistic English-like words deterministically."""
    random.seed(seed)

    prefixes = [
        "pre", "un", "dis", "in", "im", "non", "re", "sub", "inter", "trans",
        "super", "semi", "anti", "mid", "under", "over", "auto", "co", "bi", "tri"
    ]
    roots = [
        "dict", "struct", "graph", "log", "comput", "form", "port", "spect", "tract",
        "vert", "press", "fact", "rupt", "script", "ject", "sect", "mit", "ced", "plic",
        "scrib", "pel", "tend", "duc", "vid", "vis", "pend", "sens", "sent", "pon", "pos"
    ]
    suffixes = [
        "tion", "able", "ible", "ity", "ous", "al", "ment", "ness", "ful", "less",
        "ize", "ify", "ive", "ence", "ance", "er", "or", "ist", "ism", "ish"
    ]

    words: Set[str] = set()

    # Step 1: Base combinations of (prefix) + root + (suffix)
    for r in roots:
        words.add(r)
        for s in suffixes:
            words.add(f"{r}{s}")
        for p in prefixes:
            words.add(f"{p}{r}")
            for s in suffixes:
                words.add(f"{p}{r}{s}")
        if len(words) >= target_count:
            break

    # Step 2: If still needed, produce systematic compound and length-varying permutations
    chars = string.ascii_lowercase
    counter = 1
    while len(words) < target_count:
        # Generate phonetic pseudo-words with varying prefixes to simulate realistic vocabulary
        p = prefixes[counter % len(prefixes)]
        r = roots[(counter // len(prefixes)) % len(roots)]
        extra = "".join(random.choices(chars, k=3))
        w = f"{p}{r}{extra}"
        words.add(w)
        counter += 1

    result = sorted(list(words))[:target_count]
    return result


def export_benchmark_dataset(size: int) -> Path:
    """Exports a benchmark dataset to JSON."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    words = generate_unique_words(size)
    target_path = DATA_DIR / f"dataset_{size}.json"

    with open(target_path, "w", encoding="utf-8") as f:
        json.dump(words, f, indent=2)

    print(f"Generated {len(words):,} words -> {target_path}")
    return target_path


def main():
    print("=" * 60)
    print("Benchmark Dataset Generator")
    print("=" * 60)
    sizes = [1_000, 5_000, 10_000, 50_000, 100_000]
    for s in sizes:
        export_benchmark_dataset(s)
    print("=" * 60)
    print("All benchmark datasets successfully generated.")


if __name__ == "__main__":
    main()
