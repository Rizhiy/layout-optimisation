from layout_optimisation.config import cfg
from layout_optimisation.layouts.base import generate_key_map_template
from layout_optimisation.layouts.stats import generate_hand_and_row_maps

template = generate_key_map_template(cfg)

hand_map, row_map = generate_hand_and_row_maps(template, cfg)


print(row_map.nice_str(cfg))
print(hand_map.nice_str(cfg))
