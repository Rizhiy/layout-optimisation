from typing import Tuple

from .base import Finger, Hand, Keyboard, KeyMap, Layout, Row


def generate_key_map_template(cfg: dict):
    total_keys = 0
    for num_keys in Row.get_row_lengths(cfg):
        total_keys += num_keys * 2
    return KeyMap(required_length=total_keys)


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
        row_values = [getattr(Finger, value) for value in row_values]
        values += row_values[::-1] + row_values
    return template(values, "FINGERS")


def generate_penalty_map(template: KeyMap, cfg: dict, none_value=100) -> KeyMap:
    values = []
    for row in Row:
        row_penalties = cfg["key_penalties"][row.name]
        values += [cfg["left_hand_penalty"] + val for val in row_penalties[::-1]] + row_penalties
    for idx, value in enumerate(values):
        if value is None:
            values[idx] = none_value
    values = [float(val) for val in values]

    return template(values, "PENALTY")


def generate_keyboard(template: KeyMap, cfg: dict) -> Keyboard:
    hand_map, row_map = generate_hand_and_row_maps(template, cfg)
    finger_map = generate_finger_map(template, cfg)
    penalty_map = generate_penalty_map(template, cfg)
    return Keyboard(hand_map, finger_map, row_map, penalty_map)
