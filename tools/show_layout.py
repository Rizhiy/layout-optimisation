from pathlib import Path

from layout_optimisation.config import cfg
from layout_optimisation.layouts.base import Keyboard, Layout, generate_key_map_template
from layout_optimisation.layouts.layouts import BEALK, COLEMAK, QWERTY, RSTHD
from layout_optimisation.layouts.stats import generate_finger_map, generate_hand_and_row_maps
from layout_optimisation.penalty import calculate_penalties, generate_penalty_map
from layout_optimisation.utils import process_text

template = generate_key_map_template(cfg)

hand_map, row_map = generate_hand_and_row_maps(template, cfg)
finger_map = generate_finger_map(template, cfg)
penalty_map = generate_penalty_map(template, cfg)
keyboard = Keyboard(hand_map, finger_map, row_map, penalty_map)


text_path = Path(__file__).absolute().parents[1] / "texts" / "alice30.txt"
# text_path = Path(__file__).absolute().parents[1] / "layout_optimisation" / "layouts" / "base.py"

with text_path.open() as f:
    text = "".join(f.read())

text = process_text(text)
layout = RSTHD
print(layout)
layout.add_keyboard(keyboard)

penalties = calculate_penalties(text, layout)
print(penalties)
