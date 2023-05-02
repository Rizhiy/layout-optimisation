import argparse
import logging
from pathlib import Path

from layout_optimisation.annealing import run_annealing
from layout_optimisation.config import cfg

logging.basicConfig(level=logging.ERROR)

parser = argparse.ArgumentParser()
parser.add_argument("--text-dir", type=Path, default=Path(__file__).parents[1] / "texts")
parser.add_argument("--dir-weights", nargs="+")
args = parser.parse_args()

if args.dir_weights:
    if len(args.dir_weights) % 2 == 1:
        raise ValueError("Invalid dir weights")
    keys = args.dir_weights[::2]
    values = [float(val) for val in args.dir_weights[1::2]]
    dir_weights = dict(zip(keys, values))
else:
    dir_weights = cfg["dir_weights"]

best_layout = run_annealing(cfg, text_dir=args.text_dir, dir_weights=dir_weights)
print("For layouts.py:\n")
print(best_layout.for_layout(cfg))
print()
print(best_layout.format(cfg))
