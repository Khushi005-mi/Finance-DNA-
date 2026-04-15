import json
import yaml
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_DIR = BASE_DIR / "configs"


def load_industry_rules():
    with open(CONFIG_DIR / "industry_rules.json") as f:
        return json.load(f)


def load_pipeline_config():
    with open(CONFIG_DIR / "pipeline_config.yaml") as f:
        return yaml.safe_load(f)