from __future__ import annotations

import argparse
from pathlib import Path

from layout_optimisation.config import cfg


def process_text(text: str) -> str:
    # Change 4 spaces to tabs (python)
    return text.lower().replace("    ", "\t")


def complete_and_parse_args(parser: argparse.ArgumentParser) -> argparse.Namespace:
    parser.add_argument("--text-dir", type=Path, default=Path(__file__).parents[1] / "texts")
    parser.add_argument("--dir-weights", nargs="+")
    parser.add_argument("--no-forced", action="store_true", help="Don't count forced penalties")
    args = parser.parse_args()

    if args.dir_weights:
        if len(args.dir_weights) % 2 == 1:
            raise ValueError("Invalid dir weights")
        keys = args.dir_weights[::2]
        values = [float(val) for val in args.dir_weights[1::2]]
        args.dir_weights = dict(zip(keys, values))
    else:
        args.dir_weights = cfg["dir_weights"]

    return args
