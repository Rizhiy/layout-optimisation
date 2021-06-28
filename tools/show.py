import argparse
from pathlib import Path

from layout_optimisation.config import cfg
from layout_optimisation.layouts.base import Keyboard, generate_key_map_template
from layout_optimisation.layouts.layouts import LAYOUTS
from layout_optimisation.layouts.stats import generate_finger_map, generate_hand_and_row_maps
from layout_optimisation.penalty import CHARS_TO_TRACK, generate_penalty_map

parser = argparse.ArgumentParser()
parser.add_argument("name", type=str, choices=LAYOUTS.keys())
parser.add_argument("--show-penalties", action="store_true")
args = parser.parse_args()

template = generate_key_map_template(cfg)

hand_map, row_map = generate_hand_and_row_maps(template, cfg)
finger_map = generate_finger_map(template, cfg)
penalty_map = generate_penalty_map(template, cfg)
keyboard = Keyboard(hand_map, finger_map, row_map, penalty_map)

layout = LAYOUTS[args.name]
print(layout.format(cfg))
layout.add_keyboard(keyboard)
if args.show_penalties:
    print(penalty_map.format(cfg))

for char in CHARS_TO_TRACK:
    try:
        penalty = layout.get_location_penalty(char)
    except KeyError:
        print(f"Can't find {char!r} in layout")
