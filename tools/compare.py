import argparse
import logging
from pathlib import Path

import pandas as pd
from tqdm import tqdm

from layout_optimisation.config import cfg
from layout_optimisation.layouts.layouts import LAYOUTS
from layout_optimisation.penalty import evaluate

logging.basicConfig(level=logging.INFO)

parser = argparse.ArgumentParser()
parser.add_argument("names", type=str, nargs="*", default=list(LAYOUTS.keys()))
parser.add_argument("--text-dir", type=Path, default=Path(__file__).parents[1] / "texts")
parser.add_argument("--dir-weights", nargs="+", help="", default=[])
args = parser.parse_args()

if len(args.dir_weights) % 2 == 1:
    raise ValueError("Invalid dir weights")
keys = args.dir_weights[::2]
values = [float(val) for val in args.dir_weights[1::2]]
dir_weights = dict(zip(keys, values))

layout_results = {}
for name in tqdm(args.names, desc="Evaluating layouts"):
    layout_results[name] = evaluate(name, args.text_dir, cfg, dir_weights)

df = pd.DataFrame.from_dict(layout_results)
print(df)
