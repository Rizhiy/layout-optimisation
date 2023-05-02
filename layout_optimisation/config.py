from pathlib import Path

import yaml


def load_cfg(path: Path = Path(__file__).parent / "config.yaml") -> dict:
    with path.open() as f:
        return yaml.safe_load(f)


cfg = load_cfg()
