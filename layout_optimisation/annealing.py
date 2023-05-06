from __future__ import annotations

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


def run_annealing(cfg: dict, **kwargs) -> Layout:
    layouts = generate_initial_layouts(cfg)
    annealing = cfg["annealing"]
    temperature = annealing["init_temperature"]
    num_iters = annealing["num_iters"]
    iters_per_cycle = annealing["iters_per_cycle"]
    num_cycles = num_iters // iters_per_cycle
    cooling_rate = (annealing["final_temperature"] / temperature) ** (1 / num_cycles)

    template = generate_key_map_template(cfg)
    keyboard = generate_keyboard(template, cfg)
    kwargs.update({"cfg": cfg, "template": template, "keyboard": keyboard})

    outer_loop_iterator = trange(num_cycles, desc="Annealing")
    try:
        for _ in outer_loop_iterator:
            new_layouts = []
            with Pool(annealing["num_processes"]) as p:
                func = partial(anneal, temperature=temperature, num_iters=iters_per_cycle, **kwargs)
                tqdm_kwargs = dict(desc="Evaluating layouts in a pool", leave=False, total=len(layouts))
                for proc_layouts in tqdm(p.imap(func, layouts), **tqdm_kwargs):
                    proc_layouts = sorted(proc_layouts, key=itemgetter(1))
                    new_layouts.extend(proc_layouts[: annealing["keep_top"]])
            new_layouts = sorted(new_layouts, key=itemgetter(1))
            layouts = [l for l, _ in new_layouts[: annealing["num_layouts"]]]
            temperature *= cooling_rate
            outer_loop_iterator.set_description(
                f"Annealing outer loop, best score={new_layouts[0][1]:.3f}, {temperature=:.2f}"
            )
    except KeyboardInterrupt:
        logger.warning(f"Stopping optimisation due to KeyboardInterrupt")
        if outer_loop_iterator.n == 0:
            t_iter = tqdm(layouts, desc="Evaluating initial layouts due to fast exit")
            layout_energies = [(l, combine_and_evaluate(l, **kwargs)["total"]) for l in t_iter]
            layouts = [l for l, _ in sorted(layout_energies, key=itemgetter(1))]

    best_layout = Layout.from_flat(layouts[0], template, keyboard)
    return best_layout
