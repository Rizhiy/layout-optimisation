import argparse
import logging
from collections import defaultdict
from pathlib import Path

from layout_optimisation.config import cfg
from layout_optimisation.layouts.layouts import LAYOUTS
from layout_optimisation.penalty import evaluate

logging.basicConfig(level=logging.INFO)

parser = argparse.ArgumentParser()
parser.add_argument("name", type=str, choices=LAYOUTS.keys())
parser.add_argument("--text-dir", type=Path, default=Path(__file__).parents[1] / "texts")
parser.add_argument("--dir-weights", nargs="+", help="", default=[])
args = parser.parse_args()

if len(args.dir_weights) % 2 == 1:
    raise ValueError("Invalid dir weights")
keys = args.dir_weights[::2]
values = [float(val) for val in args.dir_weights[1::2]]
dir_weights = dict(zip(keys, values))

print(evaluate(args.name, args.text_dir, cfg, dir_weights))
