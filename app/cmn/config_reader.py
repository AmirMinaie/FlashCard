import json
from .resource_helper import resource_path
from pathlib import Path

class ConfigReader:
    def __init__(self, file_name="config.json"):
        self.config_path = Path(resource_path("config" , file_name ))
        self._config = None

    def load(self):
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")

        with open(self.config_path, encoding="utf-8") as f:
            self._config = json.load(f)
        return self._config

    def get(self, key, default=None):
        if self._config is None:
            self.load()
        return self._config.get(key, default)
