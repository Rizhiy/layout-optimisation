from __future__ import annotations

import copy
import logging
from collections import defaultdict
from pathlib import Path
from typing import Dict

import numpy as np
from tqdm import tqdm

from layout_optimisation.layouts.base import Finger, Layout, Row
from layout_optimisation.utils import process_text

logger = logging.getLogger(__name__)


DIGITS = set("1234567890")
LETTERS = set("qwertyuiopasdfghjklzxcvbnm")
SPECIAL = set("`!\"$%^&*()-=_+[]{};'#:@~\|,./<>?")
SPACING = {"\t", "\n", " ", "\b"}
ARROWS = {"↓", "↑", "←", "→"}
EXTRA = {"\x1b"}
CHARS_TO_TRACK = DIGITS.union(LETTERS).union(SPECIAL).union(SPACING).union(ARROWS).union(EXTRA)

GROUPS = {"writing": LETTERS.union(SPACING), "digits": DIGITS, "arrows": ARROWS, "math_operators": set("+-*/")}


def calc_long_jump(rows: np.array, sep: int = 1) -> np.array:
    top_start = rows[:-sep] == Row.TOP.value
    bot_start = rows[:-sep] == Row.BOT.value
    top_end = rows[sep:] == Row.TOP.value
    bot_end = rows[sep:] == Row.BOT.value
    long_jump = top_start & bot_end | bot_start & top_end
    return long_jump


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
    for char in tqdm(text, desc="Processing text", disable=cfg["disable_eval_tqdm"]):
        if char in missed_chars:
            continue
        if char not in CHARS_TO_TRACK and char not in missed_chars:
            logger.warning(f"Found char {char!r}, which is not tracked, skipping")
            missed_chars.add(char)
            continue
        if char not in cfg["ignore_loc_penality_for_chars"]:
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
    location_penalty += layout.get_location_penalty("\x1b") * text_len * cfg["esc_mult"]
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

    # Alternating hand four times in a row
    diff_hand = hands[:-1] != hands[1:]
    diff_hand_4 = diff_hand[2:] & diff_hand[1:-1] & diff_hand[:-2]
    alternating_hand_penalty = penalties["alternating_hand"] * np.sum(diff_hand_4) / text_len
    total += alternating_hand_penalty
    logger.info(f"Alternating hand: {alternating_hand_penalty:.3f}")

    # Long jumps
    long_jump = calc_long_jump(rows)

    # Same finger long jump
    long_jump_finger_penalty = penalties["long_jump_finger"] * np.sum(same_finger & long_jump) / text_len
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
        penalties["long_jump_consecutive"] * (np.sum(consecutive_fingers & long_jump)) / text_len
    )
    total += long_jump_consecutive_penalty
    logger.info(f"Long jump consecutive: {long_jump_consecutive_penalty:.3f}")

    # Long jump same hand
    long_jump_hand_penalty = penalties["long_jump_hand"] * (np.sum(same_hand & long_jump)) / text_len
    total += long_jump_hand_penalty
    logger.info(f"Long jump hand: {long_jump_hand_penalty:.3f}")

    # Long jump sandwich
    same_finger_2 = (fingers[:-2] == fingers[2:]) & (hands[:-2] == hands[2:])
    long_jump = calc_long_jump(rows, sep=2)
    long_jumps_sandwich_penalty = penalties["long_jump_sandwich"] * (np.sum(same_finger_2 & long_jump)) / text_len
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

    # Twist, only considering main rows here
    descending = (rows[:-2] == Row.TOP.value) & (rows[1:-1] == Row.HOM.value) & (rows[2:] == Row.BOT.value)
    ascending = (rows[:-2] == Row.BOT.value) & (rows[1:-1] == Row.HOM.value) & (rows[2:] == Row.TOP.value)
    twist = (inbound | outbound) & (ascending | descending)
    twist_penalty = penalties["twist"] * np.sum(twist) / text_len
    total += twist_penalty
    logger.info(f"Twist: {twist_penalty:.3f}")

    # Finger disbalance, count only index, middle and ring fingers

    finger_usage = {"I": i_finger, "M": m_finger, "R": r_finger}
    finger_ratios = cfg["finger_ratios"]
    finger_totals_normed = {finger: np.sum(usage) / finger_ratios[finger] for finger, usage in finger_usage.items()}
    finger_values = list(finger_totals_normed.values())
    finger_disbalance_penalty = (max(finger_values) - min(finger_values)) / text_len
    finger_disbalance_penalty *= penalties["finger_disbalance"]
    total += finger_disbalance_penalty
    logger.info(f"Finger disbalance: {finger_disbalance_penalty:.3f}")

    # Split groups, similar keys split between layers
    groups = copy.copy(GROUPS)
    groups.update({name: set(values) for name, values in cfg["extra_groups"].items()})
    split_group_penalty = 0
    for group_name, group in groups.items():
        group_layers = [layout.get_layer(char) for char in group]
        if len(set(group_layers)) > 1:
            logger.debug(f"Group {group_name} is split")
            split_group_penalty += 1
    split_group_penalty *= penalties["split_group"]
    total += split_group_penalty
    logger.info(f"Split group: {split_group_penalty:.3f}")

    # Frozen keys, kind of a hack, but an easy way to assign a key to a desired place
    frozen_keys_penalty = 0
    for char, index in cfg["frozen_keys"].items():
        if layout.flatten().index(char) != index:
            logger.debug(f"Char {char!r} is in the wrong place")
            frozen_keys_penalty += 1
    frozen_keys_penalty *= penalties["frozen_keys"]
    total += frozen_keys_penalty
    logger.info(f"Frozen keys: {frozen_keys_penalty:.3f}")

    # Blocked indexes, also a hack to prevent chars being assigned to certain positions
    blocked_indexes_penalty = 0
    for idx in cfg["blocked_indexes"]:
        if layout.flatten()[idx] is not None:
            logger.debug(f"Found key at index {idx}, which is supposed to be empty")
            blocked_indexes_penalty += 1
    blocked_indexes_penalty *= penalties["blocked_indexes"]
    total += blocked_indexes_penalty
    logger.info(f"Blocked indexes: {blocked_indexes_penalty:.3f}")

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
        "split_group": split_group_penalty,
        "frozen_keys": frozen_keys_penalty,
        "blocked_indexes": blocked_indexes_penalty,
    }


def process_and_calculate(dir_path: Path, layout: Layout, cfg: dict) -> Dict[str, float]:
    full_text = ""
    for file_path in dir_path.rglob("*"):
        if file_path.is_dir():
            continue
        with file_path.open() as f:
            lines = f.readlines()[:: cfg["text_downsampling"]]
            full_text += "".join(lines)
            full_text += "\n"
    full_text = process_text(full_text)
    if len(full_text) == 0:
        return defaultdict(float)
    return calculate_penalties(full_text, layout, cfg)


def evaluate(
    layout: Layout, text_dir: Path, cfg: dict, dir_weights: Dict[str, float] = None, no_forced=False
) -> Dict[str, float]:
    dir_weights = dir_weights or {}

    total_penalties = defaultdict(float)
    for dir_path in text_dir.glob("*"):
        if not dir_path.is_dir():
            continue
        if dir_path.name not in dir_weights:
            dir_weights[dir_path.name] = 1
        dir_weight = dir_weights[dir_path.name]
        penalties = process_and_calculate(dir_path, layout, cfg)
        for key, value in penalties.items():
            total_penalties[key] += value * dir_weight

    total_weight = sum(dir_weights.values())
    for key, value in total_penalties.items():
        total_penalties[key] = value / total_weight
    if no_forced:
        for key in ["split_group", "frozen_keys", "blocked_indexes"]:
            total_penalties["total"] -= total_penalties[key]
            del total_penalties[key]
    return total_penalties
