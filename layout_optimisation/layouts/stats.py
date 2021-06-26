from pathlib import Path
from typing import Tuple

from .base import Hand, KeyMap, Row


def generate_hand_and_row_maps(key_map: KeyMap, cfg: dict) -> Tuple[KeyMap, KeyMap]:
    hands = []
    rows = []
    for row_name, num_keys in cfg["keys_per_row"].items():
        left_hand = [Hand.L] * num_keys
        right_hand = [Hand.R] * num_keys
        row = [getattr(Row, row_name)] * num_keys * 2
        hands.extend(left_hand)
        hands.extend(right_hand)
        rows.extend(row)
    return key_map(hands), key_map(rows)
