from __future__ import annotations

import copy
from enum import Enum, auto, unique
from functools import lru_cache, partial
from typing import List

from dataclassy import dataclass

from layout_optimisation.config import load_cfg


class Finger(Enum):
    T = auto()
    I = auto()
    M = auto()
    R = auto()
    P = auto()


class Hand(Enum):
    L = auto()
    R = auto()

    def __str__(self):
        return self.name


class Row(Enum):
    NUM = auto()
    TOP = auto()
    HOM = auto()
    BOT = auto()
    MOD = auto()
    TMB = auto()

    @classmethod
    def get_row_lengths(cls, cfg: dict) -> List[int]:
        lengths = []
        for row_name in cls:
            lengths.append(cfg["keys_per_row"][row_name.name])
        return lengths

    def __str__(self):
        return self.name


class KeyMap:
    def __init__(self, required_length: int):
        self._required_length = required_length
        self._initialised = False
        self._values = None
        self._name = None

    @property
    def values(self) -> list:
        return self._values

    @values.setter
    def values(self, values: list):
        if self._initialised:
            raise ValueError("Values have already been initialised")
        assert len(values) == self._required_length, f"KeyMap should be {self._required_length} long, got {len(values)}"

        for value in values:
            if value is not None:
                first_type = type(value)
                break

        for val in values:
            assert isinstance(val, first_type) or val is None

        self._values = values
        self._initialised = True

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str):
        assert isinstance(name, str)
        self._name = name

    def __getitem__(self, idx: int):
        return self.values[idx]

    def __call__(self, values: list, name=None) -> KeyMap:
        actual = copy.copy(self)
        actual.values = values
        if name is not None:
            actual.name = name
        return actual

    def format(self, cfg: dict, push_out=True, thumb_in_the_middle=True) -> str:
        def format_value(value, length=0):
            replacements = {r"\x08": r"\b"}
            if value is None:
                value = "✕"
            if value == " ":
                value = "\s"
            value = repr(str(value))[1:-1]
            value = value.replace("\\\\", "\\")
            if value in replacements:
                value = replacements[value]
            return f"{value:^{length}}"

        result = ""
        current_idx = 0
        longest_val = len(format_value(max(self._values, key=lambda x: len(format_value(x)))))
        format_value = partial(format_value, length=longest_val)

        row_lengths = Row.get_row_lengths(cfg)
        longest_row = max(row_lengths)

        # TODO: This needs to be refactored at some point
        for idx, num_keys in enumerate(row_lengths):
            if idx == len(row_lengths) - 1 and thumb_in_the_middle:
                push_out = False
            left_values = []
            if not push_out:
                for _ in range(longest_row - num_keys):
                    left_values.append(format_value(""))
            for _ in range(num_keys):
                left_values.append(format_value(self.values[current_idx]))
                current_idx += 1
            if push_out:
                for _ in range(longest_row - num_keys):
                    left_values.append(format_value(""))
            right_values = []
            if push_out:
                for _ in range(longest_row - num_keys):
                    right_values.append(format_value(""))
            for _ in range(num_keys):
                right_values.append(format_value(self.values[current_idx]))
                current_idx += 1
            if not push_out:
                for _ in range(longest_row - num_keys):
                    right_values.append(format_value(""))
            result += f"{' '.join(left_values)} | {' '.join(right_values)}\n"
        if self._name:
            rows = result.split("\n")
            max_len = len(max(rows, key=len)) - len(self._name)
            pad = len(self._name) % 2 == 0
            header = "=" * (max_len // 2 - 1) + f" {self._name} " + "=" * (max_len // 2 - int(not pad)) + "\n"
            result = header + result

        return result


class Keyboard:
    def __init__(self, hands: KeyMap, fingers: KeyMap, rows: KeyMap, penalties: KeyMap):
        self._hands = hands
        self._fingers = fingers
        self._rows = rows
        self._penalties = penalties


class Layout:
    def __init__(self, layers: List[KeyMap], keyboard: Keyboard = None):
        self._layers = layers
        self._char_map = {}
        for layer_idx, layer in enumerate(self._layers):
            for value in layer.values:
                if value in self._char_map and value is not None:
                    raise ValueError(f"Multiple instances of same key are not currently supported: {value}")
                self._char_map[value] = layer_idx

        self._keyboard = keyboard

    def add_keyboard(self, keyboard: Keyboard):
        if self._keyboard is not None:
            raise ValueError(f"Keyboard was already added")
        self._keyboard = keyboard

    def format(self, cfg: dict) -> str:
        result = ""
        for idx, layer in enumerate(self._layers):
            result += f"Layer {idx}:\n"
            result += layer.format(cfg) + "\n"
        return result

    @lru_cache(maxsize=512)
    def get_layer(self, char: str) -> KeyMap:
        return self._layers[self._char_map[char]]

    @lru_cache(maxsize=512)
    def get_layer_idx(self, char: str) -> int:
        return self._layers.index(self.get_layer(char))

    @lru_cache(maxsize=512)
    def get_index(self, char: str) -> int:
        return self.get_layer(char).values.index(char)

    @lru_cache(maxsize=512)
    def get_hand(self, char: str) -> Hand:
        return self._keyboard._hands[self.get_index(char)]

    @lru_cache(maxsize=512)
    def get_finger(self, char: str) -> Finger:
        return self._keyboard._fingers[self.get_index(char)]

    @lru_cache(maxsize=512)
    def get_row(self, char: str) -> Finger:
        return self._keyboard._rows[self.get_index(char)]

    @lru_cache(maxsize=512)
    def get_location_penalty(self, char: str) -> int:
        return self._keyboard._penalties[self.get_index(char)]


def generate_key_map_template(cfg: dict):
    total_keys = 0
    for num_keys in Row.get_row_lengths(cfg):
        total_keys += num_keys * 2
    return KeyMap(required_length=total_keys)
