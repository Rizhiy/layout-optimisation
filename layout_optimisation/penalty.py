import logging
from collections import defaultdict
from pathlib import Path
from typing import Dict, Tuple

import numpy as np
from tqdm import tqdm

from layout_optimisation.layouts.base import Finger, Keyboard, KeyMap, Layout, Row, generate_key_map_template
from layout_optimisation.layouts.layouts import LAYOUTS
from layout_optimisation.layouts.stats import generate_finger_map, generate_hand_and_row_maps
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


LOWER_CASE = set(r"`1234567890-=qwertyuiop[]asdfghjkl;'#\zxcvbnm,./")
UPPER_CASE = set(r'~!@#$%^&*()_+QWERTYUIOP{}ASDFGHJKL:"|ZXCVBNM<>?')
SPACING = {"\t", "\n", " ", "\b"}
ARROWS = {"↓", "↑", "←", "→"}
CHARS_TO_TRACK = LOWER_CASE.union(UPPER_CASE).union(SPACING).union(ARROWS)


def calc_long_jump(rows: np.array, sep: int = 1) -> Tuple[np.array, np.array, np.array]:
    num_start = rows[:-sep] == Row.NUM.value
    top_start = rows[:-sep] == Row.TOP.value
    hom_start = rows[:-sep] == Row.HOM.value
    bot_start = rows[:-sep] == Row.BOT.value
    mod_start = rows[:-sep] == Row.MOD.value
    num_end = rows[sep:] == Row.NUM.value
    top_end = rows[sep:] == Row.TOP.value
    hom_end = rows[sep:] == Row.HOM.value
    bot_end = rows[sep:] == Row.BOT.value
    mod_end = rows[sep:] == Row.MOD.value
    super_long_jump = num_start & mod_end | mod_start & num_end
    very_long_jump = num_start & bot_end | top_start & mod_end | bot_start & num_end | mod_start & top_end
    long_jump = (
        num_start & hom_end
        | top_start & bot_end
        | hom_start & mod_end
        | hom_start & num_end
        | bot_start & top_end
        | mod_start & hom_end
    )
    return super_long_jump, very_long_jump, long_jump


def calculate_penalties(text: str, layout: Layout, cfg: dict) -> Dict[str, float]:
    if len(text) == 0:
        raise ValueError(f"Passed empty text into calculate_penalties")
    location_penalty = 0
    chars = []
    hands = []
    fingers = []
    rows = []
    layers = []

    missed_chars = set()
    for char in tqdm(text, desc="Processing text"):
        if char in missed_chars:
            continue
        if char not in CHARS_TO_TRACK and char not in missed_chars:
            logger.warning(f"Found char {char!r}, which is not tracked, skipping")
            missed_chars.add(char)
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

    text_len = len(chars)

    penalties = cfg["penalties"]
    logger.info("Calculating penalties")
    location_penalty += layout.get_location_penalty("\b") * text_len * cfg["backspace_mult"]
    arrow_costs = [layout.get_location_penalty(char) for char in ARROWS]
    location_penalty += np.sum(arrow_costs) / 4 * text_len * cfg["arrow_mult"]
    location_penalty = penalties["location"] * location_penalty / text_len
    total = location_penalty
    logger.info(f"Location: {location_penalty:.3f}")

    layer_penalty = 0
    for layerd_idx, layer_cost in enumerate(penalties["layers"]):
        layer_penalty += np.sum(layers == layerd_idx) * layer_cost / text_len
    total += layer_penalty
    logger.info(f"Layers: {layer_penalty:.3f}")

    # Same finger different characters
    same_finger = (fingers[:-1] == fingers[1:]) & (hands[:-1] & hands[1:])
    diff_char = chars[:-1] != chars[1:]
    same_finger_different_key = same_finger & diff_char
    same_finger_penalty = penalties["same_finger"] * np.sum(same_finger_different_key) / text_len
    total += same_finger_penalty
    logger.info(f"Same finger: {same_finger_penalty:.3f}")

    # Same hand four times in a row
    same_hand = hands[:-1] == hands[1:]
    same_hand_4 = same_hand[2:] & same_hand[1:-1] & same_hand[:-2]
    same_hand_penalty = penalties["same_hand"] * np.sum(same_hand_4) / text_len
    total += same_hand_penalty
    logger.info(f"Same hand: {same_hand_penalty:.3f}")

    # Alternating hand three times in a row
    diff_hand = hands[:-1] != hands[1:]
    diff_hand_3_times = diff_hand[2:] & diff_hand[1:-1] & diff_hand[:-2]
    alternating_hand_penalty = penalties["alternating_hand"] * np.sum(diff_hand_3_times) / text_len
    total += alternating_hand_penalty
    logger.info(f"Alternating hand: {alternating_hand_penalty:.3f}")

    # Long jumps
    super_long_jump, very_long_jump, long_jump = calc_long_jump(rows)

    # Same finger long jump
    long_jump_finger_penalty = (
        penalties["long_jump_finger"]
        * (
            np.sum(same_finger & super_long_jump) * 2
            + np.sum(same_finger & very_long_jump) * 1.5
            + np.sum(same_finger & long_jump)
        )
        / text_len
    )
    total += long_jump_finger_penalty
    logger.info(f"Long jump finger: {long_jump_finger_penalty:.3f}")

    # Consecutive fingers long jump
    i_finger = fingers == Finger.I.value
    m_finger = fingers == Finger.M.value
    r_finger = fingers == Finger.R.value
    p_finger = fingers == Finger.P.value
    consecutive_fingers = (
        i_finger[:-1] & m_finger[1:]
        | m_finger[:-1] & r_finger[1:]
        | r_finger[:-1] & p_finger[1:]
        | p_finger[:-1] & r_finger[1:]
        | r_finger[:-1] & m_finger[1:]
        | m_finger[:-1] & i_finger[1:]
    ) & same_hand
    long_jump_consecutive_penalty = (
        penalties["long_jump_consecutive"]
        * (
            np.sum(consecutive_fingers & super_long_jump) * 2
            + np.sum(consecutive_fingers & very_long_jump) * 1.5
            + np.sum(consecutive_fingers & long_jump)
        )
        / text_len
    )
    total += long_jump_consecutive_penalty
    logger.info(f"Long jump consecutive: {long_jump_consecutive_penalty:.3f}")

    # Long jump same hand
    long_jump_hand_penalty = (
        penalties["long_jump_hand"]
        * (
            np.sum(same_hand & super_long_jump) * 2
            + np.sum(same_hand & very_long_jump) * 1.5
            + np.sum(same_hand & long_jump)
        )
        / text_len
    )
    total += long_jump_hand_penalty
    logger.info(f"Long jump hand: {long_jump_hand_penalty:.3f}")

    # Long jump sandwich
    same_finger_2 = (fingers[:-2] == fingers[2:]) & (hands[:-2] == hands[2:])
    super_long_jump, very_long_jump, long_jump = calc_long_jump(rows, sep=2)
    long_jumps_sandwich_penalty = (
        penalties["long_jump_sandwich"]
        * (
            np.sum(same_finger_2 & super_long_jump) * 2
            + np.sum(same_finger_2 & very_long_jump) * 1.5
            + np.sum(same_finger_2 & long_jump)
        )
        / text_len
    )
    total += long_jumps_sandwich_penalty
    logger.info(f"Long jump sandwich: {long_jumps_sandwich_penalty:.3f}")
    # Rolls
    same_row = rows[:-1] == rows[1:]
    same_row_3 = same_row[:-1] & same_row[1:]
    same_hand_3 = same_hand[:-1] & same_hand[1:]
    inbound = p_finger[:-2] & r_finger[1:-1] & m_finger[2:] | r_finger[:-2] & m_finger[1:-1] & i_finger[2:]
    outbound = i_finger[:-2] & m_finger[1:-1] & r_finger[2:] | m_finger[:-2] & r_finger[1:-1] & p_finger[2:]
    inbound = inbound & same_hand_3
    outbound = outbound & same_hand_3
    roll_in = inbound & same_row_3
    roll_out = outbound & same_row_3
    roll_in_penalty = np.sum(roll_in) * penalties["roll_in"] / text_len
    roll_out_penalty = np.sum(roll_out) * penalties["roll_out"] / text_len
    total += roll_in_penalty + roll_out_penalty
    logger.info(f"Rolls, in: {roll_in_penalty:.3f}; out: {roll_out_penalty:.3f}")

    # Roll reversal
    roll_reversal = (
        (
            r_finger[:-2] & p_finger[1:-1] & m_finger[2:]
            | m_finger[:-2] & r_finger[1:-1] & i_finger[2:]
            | m_finger[:-2] & i_finger[1:-1] & r_finger[2:]
            | r_finger[:-2] & m_finger[1:-1] & p_finger[2:]
        )
        & same_hand_3
        & same_row_3
    )
    roll_reversal_penalty = penalties["roll_reversal"] * np.sum(roll_reversal) / text_len
    total += roll_reversal_penalty
    logger.info(f"Roll reversal: {roll_reversal_penalty:.3f}")

    # Twist, only considering main rows here, hopefully other rows are penalised sufficiently on their own
    descending = (rows[:-2] == Row.TOP.value) & (rows[1:-1] == Row.HOM.value) & (rows[2:] == Row.BOT.value)
    ascending = (rows[:-2] == Row.BOT.value) & (rows[1:-1] == Row.HOM.value) & (rows[2:] == Row.TOP.value)
    twist = (inbound | outbound) & (ascending | descending)
    twist_penalty = penalties["twist"] * np.sum(twist) / text_len
    total += twist_penalty
    logger.info(f"Twist: {twist_penalty:.3f}")

    # Finger disbalance, count only index middle and ring fingers
    i_m_r = np.sum(i_finger), np.sum(m_finger), np.sum(r_finger)
    finger_disbalance_penalty = (max(i_m_r) - min(i_m_r)) / text_len
    total += finger_disbalance_penalty
    logger.info(f"Finger disbalance: {finger_disbalance_penalty}")

    return {
        "total": total,
        "location": location_penalty,
        "layers": layer_penalty,
        "same_finger": same_finger_penalty,
        "same_hand": same_hand_penalty,
        "alternating_hand": alternating_hand_penalty,
        "long_jump_finger": long_jump_finger_penalty,
        "long_jump_consecutive": long_jump_consecutive_penalty,
        "long_jump_sandwich": long_jumps_sandwich_penalty,
        "long_jump_hand": long_jump_hand_penalty,
        "roll_in": roll_in_penalty,
        "roll_out": roll_out_penalty,
        "roll_reversal": roll_reversal_penalty,
        "twist": twist_penalty,
        "finger_disbalance": finger_disbalance_penalty,
    }


def process_and_calculate(dir_path: Path, layout: Layout, cfg: dict) -> Dict[str, float]:
    full_text = ""
    for file_path in dir_path.rglob("*"):
        if file_path.is_dir():
            continue
        with file_path.open() as f:
            full_text += "".join(f.readlines())
            full_text += "\n"
    full_text = process_text(full_text)
    if len(full_text) == 0:
        return defaultdict(float)
    return calculate_penalties(full_text, layout, cfg)


def evaluate(name: str, text_dir: Path, cfg: dict, dir_weights: Dict[str, float] = None) -> Dict[str, float]:
    dir_weights = dir_weights or {}
    layout = LAYOUTS[name]
    template = generate_key_map_template(cfg)

    hand_map, row_map = generate_hand_and_row_maps(template, cfg)
    finger_map = generate_finger_map(template, cfg)
    penalty_map = generate_penalty_map(template, cfg)
    keyboard = Keyboard(hand_map, finger_map, row_map, penalty_map)

    layout.add_keyboard(keyboard)

    total_penalties = defaultdict(int)
    num_dirs = 0
    for dir_path in text_dir.glob("*"):
        if not dir_path.is_dir():
            continue
        dir_weight = dir_weights.get(dir_path.name, 1)
        penalties = process_and_calculate(dir_path, layout, cfg)
        for key, value in penalties.items():
            total_penalties[key] += value * dir_weight
        num_dirs += 1

    for key, value in total_penalties.items():
        total_penalties[key] = value / num_dirs
    return total_penalties
