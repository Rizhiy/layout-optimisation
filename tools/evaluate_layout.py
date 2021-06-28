import argparse
import logging
from collections import defaultdict
from pathlib import Path

from layout_optimisation.config import cfg
from layout_optimisation.layouts.base import Keyboard, Layout, generate_key_map_template
from layout_optimisation.layouts.layouts import LAYOUTS
from layout_optimisation.layouts.stats import generate_finger_map, generate_hand_and_row_maps
from layout_optimisation.penalty import calculate_penalties, generate_penalty_map, process_and_calculate
from layout_optimisation.utils import process_text

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

template = generate_key_map_template(cfg)

hand_map, row_map = generate_hand_and_row_maps(template, cfg)
finger_map = generate_finger_map(template, cfg)
penalty_map = generate_penalty_map(template, cfg)
keyboard = Keyboard(hand_map, finger_map, row_map, penalty_map)

layout = LAYOUTS[args.name]
layout.add_keyboard(keyboard)

total_penalties = defaultdict(int)
num_dirs = 0
for dir_path in args.text_dir.glob("*"):
    if not dir_path.is_dir():
        continue
    dir_weight = dir_weights.get(dir_path.name, 1)
    penalties = process_and_calculate(dir_path, layout, cfg)
    for key, value in penalties.items():
        total_penalties[key] += value * dir_weight
    num_dirs += 1

for key, value in total_penalties.items():
    total_penalties[key] = value / num_dirs
print(total_penalties)
