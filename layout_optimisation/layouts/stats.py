from pathlib import Path
from typing import Tuple

from .base import Finger, Hand, KeyMap, Row


def generate_hand_and_row_maps(template: KeyMap, cfg: dict) -> Tuple[KeyMap, KeyMap]:
    hands = []
    rows = []
    for row_name, num_keys in cfg["keys_per_row"].items():
        left_hand = [Hand.L] * num_keys
        right_hand = [Hand.R] * num_keys
        row = [getattr(Row, row_name)] * num_keys * 2
        hands.extend(left_hand)
        hands.extend(right_hand)
        rows.extend(row)
    return template(hands, "HANDS"), template(rows, "ROWS")


def generate_finger_map(template: KeyMap, cfg: dict) -> KeyMap:
    values = []
    for row in Row:
        row_values = cfg["fingers"][row.name]
        values += row_values[::-1] + row_values
    return template(values, "FINGERS")
