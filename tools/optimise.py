import argparse
import logging
from pathlib import Path

from layout_optimisation.annealing import run_annealing
from layout_optimisation.config import cfg
from layout_optimisation.layouts.layouts import LAYOUTS
from layout_optimisation.layouts.mapper import generate_key_map_template, generate_keyboard

logging.basicConfig(level=logging.ERROR)

parser = argparse.ArgumentParser()
parser.add_argument("--text-dir", type=Path, default=Path(__file__).parents[1] / "texts")
parser.add_argument("--dir-weights", nargs="+", help="", default=[])
args = parser.parse_args()

if len(args.dir_weights) % 2 == 1:
    raise ValueError("Invalid dir weights")
keys = args.dir_weights[::2]
values = [float(val) for val in args.dir_weights[1::2]]
dir_weights = dict(zip(keys, values))

template = generate_key_map_template(cfg)
keyboard = generate_keyboard(template, cfg)

best_layout = run_annealing(cfg, template=template, keyboard=keyboard, text_dir=args.text_dir, dir_weights=dir_weights)
print(best_layout.format(cfg))
