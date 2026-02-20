import yaml
import json

class Config:
    def __init__(self, config_dict):
        self.experiment = config_dict.get("experiment", {})
        self.data = config_dict.get("data", {})
        
    def __reper__(self):
        return f"Config(experiment={self.experiment}, data={self.data})"
     

def load_config(config_path="config.yaml"):
    with open(config_path, "r") as file:
        config = yaml.safe_load(file)
    config = Config(config)
    return config

def get_last_row(jsonl_path):
    with open(jsonl_path, "r", encoding="utf8") as f:
        lines = [line.strip() for line in f if line.strip()]

    if not lines:
        return None

    return json.loads(lines[-1])