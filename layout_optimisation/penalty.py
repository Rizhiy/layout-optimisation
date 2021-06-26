import logging
from enum import Enum
from typing import Dict

from tqdm import tqdm

from layout_optimisation.layouts.base import KeyMap, Layout, Row

logger = logging.getLogger(__name__)


def generate_penalty_map(template: KeyMap, cfg: dict, none_value=100) -> KeyMap:
    values = []
    for row in Row:
        row_penalties = cfg["key_penalties"][row.name]
        values += row_penalties[::-1] + row_penalties
    for idx, value in enumerate(values):
        if value is None:
            values[idx] = none_value
    values = [float(val) for val in values]

    return template(values, "PENALTY")


CHARS_TO_TRACK = set(r"`1234567890-=qwertyuiop[]asdfghjkl;'#\zxcvbnm,./'").union(set(r'¬!"£$%^&*()_+{}:@~|?<>'))
CHARS_TO_TRACK = CHARS_TO_TRACK.union({"\t", "\n", "\b", " "})


def calculate_penalties(text: str, layout: Layout) -> Dict[str, float]:
    location_penalty = 0
    hands = []
    fingers = []
    rows = []
    layers = []

    for char in tqdm(text, desc="Processing text"):
        if char not in CHARS_TO_TRACK:
            logger.warning(f"Found char {char}, which is not tracked, skipping")
            continue
        location_penalty += layout.get_location_penalty(char)
        hands.append(layout.get_hand(char))
        fingers.append(layout.get_finger(char))
        rows.append(layout.get_row(char))
        layers.append(layout.get_layer_idx(char))

    total = location_penalty
    return {"total": total, "location_penalty": location_penalty}
