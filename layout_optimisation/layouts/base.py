from __future__ import annotations

import copy
from enum import Enum, auto, unique
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

    @property
    def values(self) -> list:
        return self._values

    @values.setter
    def values(self, values: list):
        if self._initialised:
            raise ValueError("Values have already been initialised")
        assert len(values) == self._required_length
        first_type = type(values[0])
        for val in values:
            assert isinstance(val, first_type) or val is None
        self._values = values
        self._initialised = True

    def __call__(self, values: list) -> KeyMap:
        actual = copy.copy(self)
        actual.values = values
        return actual

    def nice_str(self, cfg: dict) -> str:
        result = ""
        current_idx = 0
        longest_val = len(str(max(self._values, key=lambda x: len(str(x)))))

        def format_value(value):
            if value is None:
                value = ""
            return f" {value:^{longest_val}} "

        row_lengths = Row.get_row_lengths(cfg)
        longest_row = max(row_lengths)

        for num_keys in row_lengths:
            for _ in range(longest_row - num_keys):
                result += format_value("")
            for _ in range(num_keys):
                result += format_value(self.values[current_idx])
                current_idx += 1
            result += "|"
            for _ in range(num_keys):
                result += format_value(self.values[current_idx])
                current_idx += 1
            for _ in range(longest_row - num_keys):
                result += format_value("")
            result += "\n"
        return result


class Layout:
    def __init__(self, layers: List[KeyMap]):
        self._layers = layers


def generate_key_map_template(cfg: dict):
    total_keys = 0
    for num_keys in Row.get_row_lengths(cfg):
        total_keys += num_keys * 2
    return KeyMap(required_length=total_keys)
