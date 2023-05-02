import argparse
import logging

from layout_optimisation.config import cfg
from layout_optimisation.layouts.base import Layout
from layout_optimisation.layouts.layouts import LAYOUTS
from layout_optimisation.layouts.mapper import generate_key_map_template, generate_keyboard
from layout_optimisation.penalty import evaluate
from layout_optimisation.utils import complete_and_parse_args

logging.basicConfig(level=logging.INFO)

parser = argparse.ArgumentParser()
parser.add_argument("name", type=str, choices=LAYOUTS.keys())
args = complete_and_parse_args(parser)

layout = LAYOUTS[args.name]
template = generate_key_map_template(cfg)
keyboard = generate_keyboard(template, cfg)
flat_keys = layout.flatten()
layout = Layout.from_flat(flat_keys, template)
layout.add_keyboard(keyboard)

print(evaluate(layout, args.text_dir, cfg, args.dir_weights, args.no_forced))
