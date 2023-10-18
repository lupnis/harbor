from pathlib import Path
import os
import json


class ConfigHandler:
    def __init__(self, config_path, root_key=None, not_exists_callback = None):
        self.config_path = str(Path(config_path).absolute())
        self.restore_callback = not_exists_callback
        self.root_key = root_key
        self.config_instance = {}
        self.config_node_root = {}
        self.load()

    def load(self):
        if not os.path.exists(self.config_path):
            if self.restore_callback is not None:
                self.config_instance = self.restore_callback()
            self.save()
            
        with open(self.config_path, "r") as f:
            self.config_instance = json.loads(f.read())

        self.config_node_root = self.config_instance
        if self.root_key is not None:
            for item in self.root_key.split("/"):
                self.config_node_root = self.config_node_root[item]

    def get(self, key, repl=None):
        return self.config_node_root.get(key, repl)

    def set(self, key, value):
        self.config_node_root[key] = value

    def save(self):
        with open(self.config_path, "w") as f:
            f.writelines(json.dumps(self.config_instance, indent=4))

    def save_as(self, path=None):
        with open(
            self.config_path if path is None else str(Path(path).absolute()), "w"
        ) as f:
            f.writelines(json.dumps(self.config_instance, indent=4))
