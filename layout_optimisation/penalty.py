import logging
from enum import Enum
from pathlib import Path
from typing import Dict, Tuple

import numpy as np
from tqdm import tqdm

from layout_optimisation.layouts.base import KeyMap, Layout, Row
from layout_optimisation.utils import process_text

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


def calculate_penalties(text: str, layout: Layout, cfg: dict) -> Dict[str, float]:
    location_penalty = 0
    chars = []
    hands = []
    fingers = []
    rows = []
    layers = []

    for char in tqdm(text, desc="Processing text"):
        if char not in CHARS_TO_TRACK:
            logger.warning(f"Found char {char!r}, which is not tracked, skipping")
            continue
        location_penalty += layout.get_location_penalty(char)
        chars.append(char)
        hands.append(layout.get_hand(char).value)
        fingers.append(layout.get_finger(char).value)
        rows.append(layout.get_row(char).value)
        layers.append(layout.get_layer_idx(char))

    logger.info("Making arrays")
    chars = np.array(chars)
    logger.info("Chars done")
    hands = np.array(hands)
    logger.info("Hands done")
    fingers = np.array(fingers)
    logger.info("Fingers done")
    rows = np.array(rows)
    logger.info("Rows done")
    layers = np.array(layers)
    logger.info("Layers done")

    logger.info("Calculating penalties")

    # Same finger different characters
    same_finger = fingers[:-1] == fingers[1:]
    same_char = chars[:-1] == chars[1:]
    same_finger_different_key = same_finger & (1 - same_char)
    same_finger_penalty = cfg["penalties"]["same_finger"] * np.sum(same_finger_different_key)
    logger.info("Same finger done")

    total = location_penalty

    return {"total": total, "location": location_penalty, "same_finger": same_finger_penalty}


def process_and_calculate(dir_path: Path, layout: Layout, cfg: dict) -> Tuple[Dict[str, float], int]:
    full_text = ""
    for file_path in dir_path.rglob("*"):
        # if file_path.name == "books.txt":
        #     continue
        if file_path.is_dir():
            continue
        with file_path.open() as f:
            full_text += "".join(f.readlines())
            full_text += "\n"
    full_text = process_text(full_text)
    return calculate_penalties(full_text, layout, cfg), len(full_text)
