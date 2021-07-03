import argparse
from collections import defaultdict
from operator import itemgetter
from pathlib import Path
from typing import Dict

from layout_optimisation.config import cfg
from layout_optimisation.stats import calc_char_freq
from layout_optimisation.utils import complete_and_parse_args, process_text


def process_and_calc(text_dir: Path, cfg: dict, dir_weights: Dict[str, float] = None) -> Dict[str, float]:
    dir_weights = dir_weights or {}

    final_freqs = defaultdict(float)
    for dir_path in text_dir.glob("*"):
        if not dir_path.is_dir():
            continue
        if dir_path.name not in dir_weights:
            dir_weights[dir_path.name] = 1
        dir_weight = dir_weights[dir_path.name]
        full_text = ""
        dir_weight = dir_weights[dir_path.name]
        for file_path in dir_path.rglob("*"):
            if file_path.is_dir():
                continue
            with file_path.open() as f:
                lines = f.readlines()[:: cfg["text_downsampling"]]
                full_text += "".join(lines)
                full_text += "\n"
        full_text = process_text(full_text)
        freqs = calc_char_freq(full_text)
        for char, freq in freqs.items():
            final_freqs[char] += freq * dir_weight
    total_weight = sum(dir_weights.values())
    for char, freq in final_freqs.items():
        final_freqs[char] = freq / total_weight
    final_freqs["\x1b"] = cfg["esc_mult"]
    final_freqs["\b"] = cfg["backspace_mult"]
    return final_freqs


parser = argparse.ArgumentParser()
args = complete_and_parse_args(parser)

freqs = process_and_calc(args.text_dir, cfg, args.dir_weights)
for char, freq in sorted(freqs.items(), key=itemgetter(1), reverse=True):
    if freq < 0.001:
        continue
    print(f"{char!r:6s} = {freq:.3f}")
