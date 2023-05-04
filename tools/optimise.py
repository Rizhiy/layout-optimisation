import argparse
import logging
from pathlib import Path

from layout_optimisation.annealing import run_annealing
from layout_optimisation.config import cfg
from layout_optimisation.utils import complete_and_parse_args

logging.basicConfig(level=logging.ERROR)

parser = argparse.ArgumentParser()
args = complete_and_parse_args(parser)


best_layout = run_annealing(cfg, text_dir=args.text_dir, dir_weights=args.dir_weights)
print("For layouts.py:\n")
print(best_layout.for_layout(cfg))
print()
print(best_layout.format(cfg))
