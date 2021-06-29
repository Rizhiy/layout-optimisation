import copy
import logging
import math
import random
from functools import partial
from multiprocessing import Pool
from operator import itemgetter
from pathlib import Path
from typing import Dict, List, Tuple

from tqdm import tqdm, trange

from layout_optimisation.layouts.base import Keyboard, KeyMap, Layout
from layout_optimisation.layouts.mapper import generate_key_map_template, generate_keyboard
from layout_optimisation.penalty import evaluate

from .layouts.layouts import LAYOUTS

logger = logging.getLogger(__name__)

# http://mkweb.bcgsc.ca/carpalx/?simulated_annealing
def generate_initial_layouts(cfg: dict) -> List[List[str]]:
    template = generate_key_map_template(cfg)
    keyboard = generate_keyboard(template, cfg)

    total_keys = len(template) * cfg["annealing"]["num_layers"]
    layouts = []
    for l_name, layout in LAYOUTS.items():
        flat_keys = layout.flatten(total_keys)
        try:
            Layout.from_flat(flat_keys, template, keyboard)
        except ValueError:
            logger.warning(f"Couldn't flatten {l_name}")
            continue
        layouts.append(flat_keys)

    while len(layouts) < cfg["annealing"]["num_layouts"]:
        new_keys = copy.copy(layouts[-1])
        random.shuffle(new_keys)
        layouts.append(new_keys)
    return layouts


def combine_and_evaluate(
    flat_keys: List[str],
    template: KeyMap,
    keyboard: Keyboard,
    text_dir: Path,
    cfg: dict,
    dir_weights: Dict[str, float] = None,
) -> float:
    layout = Layout.from_flat(flat_keys, template, keyboard)
    return evaluate(layout, text_dir, cfg, dir_weights)


def anneal(flat_keys: List[str], temperature: float, num_iters: int, **kwargs) -> List[Tuple[List[str], float]]:
    prev_energy = combine_and_evaluate(flat_keys, **kwargs)["total"]
    best_layouts = [(flat_keys, prev_energy)]
    for _ in trange(num_iters, desc="Annealing", disable=True):
        new_keys = copy.copy(flat_keys)
        first_idx = random.randint(0, len(new_keys) - 1)
        second_idx = random.randint(0, len(new_keys) - 1)
        new_keys[first_idx], new_keys[second_idx] = new_keys[second_idx], new_keys[first_idx]
        new_energy = combine_and_evaluate(new_keys, **kwargs)["total"]
        d_e = new_energy - prev_energy
        if d_e < 0 or math.exp(-d_e / temperature) > random.uniform(0, 1):
            prev_energy = new_energy
            flat_keys = new_keys
            best_layouts.append((flat_keys, prev_energy))
    return best_layouts


def run_annealing(cfg: dict, **kwargs) -> List[Layout]:
    layouts = generate_initial_layouts(cfg)
    annealing = cfg["annealing"]
    temperature = annealing["init_temperature"]
    num_iters = annealing["num_iters"]
    iters_per_cycle = annealing["iters_per_cycle"]
    kwargs.update({"cfg": cfg})

    t = trange(num_iters // iters_per_cycle, desc="Annealing")
    for _ in t:
        with Pool(annealing["num_processes"]) as p:
            func = partial(anneal, temperature=temperature, num_iters=iters_per_cycle, **kwargs)
            stacked_layouts = p.map(func, layouts)
        new_layouts = []
        for proc_layouts in stacked_layouts:
            proc_layouts = sorted(proc_layouts, key=itemgetter(1))
            new_layouts.extend(proc_layouts[: annealing["keep_top"]])
        new_layouts = sorted(new_layouts, key=itemgetter(1))
        t.set_description(f"Annealing outer loop, best score={new_layouts[0][1]:.3f}")
        layouts = [l for l, _ in new_layouts[: annealing["num_layouts"]]]
        temperature *= math.exp(-iters_per_cycle * annealing["cooling_rate"] / num_iters)

    best_layout = Layout.from_flat(layouts[0], kwargs["template"], kwargs["keyboard"])
    return best_layout
