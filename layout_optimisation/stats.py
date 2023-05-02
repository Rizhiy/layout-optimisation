from __future__ import annotations

from collections import defaultdict

from tqdm import tqdm


def calc_char_freq(text: str):
    counts = defaultdict(int)
    for char in tqdm(text, desc="Calculating frequencies"):
        counts[char] += 1
    total = len(text)
    frequencies = {char: count / total for char, count in counts.items()}
    return frequencies
