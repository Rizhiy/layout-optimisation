import argparse
import logging

import pandas as pd
from tqdm import tqdm

from layout_optimisation.config import cfg
from layout_optimisation.layouts.layouts import LAYOUTS
from layout_optimisation.layouts.mapper import generate_key_map_template, generate_keyboard
from layout_optimisation.penalty import evaluate
from layout_optimisation.utils import complete_and_parse_args

logging.basicConfig(level=logging.ERROR)

parser = argparse.ArgumentParser()
parser.add_argument("names", type=str, nargs="*", default=list(LAYOUTS.keys()))
args = complete_and_parse_args(parser)


# These penalties are optimisation constraints, rather than real metrics
cfg["penalties"]["frozen_keys"] = 0
cfg["penalties"]["blocked_indexes"] = 0

template = generate_key_map_template(cfg)
keyboard = generate_keyboard(template, cfg)

layout_results = {}
for name in tqdm(args.names, desc="Evaluating layouts"):
    layout = LAYOUTS[name]
    layout.add_keyboard(keyboard)
    layout_results[name] = evaluate(layout, args.text_dir, cfg, args.dir_weights, args.no_forced)

df = pd.DataFrame.from_dict(layout_results)
print(df)
