import argparse
from pathlib import Path


def process_text(text: str) -> str:
    # Change 4 spaces to tabs (python)
    return text.lower().replace("    ", "\t")


def complete_and_parse_args(parser: argparse.ArgumentParser) -> argparse.Namespace:
    parser.add_argument("--text-dir", type=Path, default=Path(__file__).parents[1] / "texts")
    parser.add_argument("--dir-weights", nargs="+", help="", default=[])
    parser.add_argument("--no-forced", action="store_true", help="Don't count forced penalties")
    args = parser.parse_args()

    if len(args.dir_weights) % 2 == 1:
        raise ValueError("Invalid dir weights")
    keys = args.dir_weights[::2]
    values = [float(val) for val in args.dir_weights[1::2]]
    dir_weights = dict(zip(keys, values))
    args.dir_weights = dir_weights
    return args
