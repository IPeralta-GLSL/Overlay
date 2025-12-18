import json
import os
from PySide6.QtCore import QStandardPaths

APP_VERSION = "1.1.0"

class ConfigManager:
    def __init__(self):
        self.config_dir = QStandardPaths.writableLocation(QStandardPaths.AppConfigLocation)
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
        self.config_file = os.path.join(self.config_dir, "config.json")
        self.default_config = {
            "font_family": "Arial",
            "font_size": 14,
            "text_color": "#4CAF50",
            "background_color": "#2b2b2b",
            "background_opacity": 0.8,
            "update_interval_ms": 1000,
            "position_x": 10,
            "position_y": 10,
            "position_preset": "top-left",
            "position_locked": False,
            "language": "es",
            "show_time": True,
            "show_cpu": True,
            "show_ram": True,
            "show_gpu": True,
            "show_cpu_temp": False,
            "show_gpu_temp": False,
            "show_cpu_name": False,
            "show_gpu_name": False,
            "show_cpu_manufacturer": False,
            "show_gpu_manufacturer": False,
            "dynamic_colors": False,
            "color_only_value": False,
            "color_low": "#4CAF50",
            "color_medium": "#FFC107",
            "color_high": "#F44336",
            "hotkey_toggle": "ctrl+shift+o",
            "hotkey_enabled": True,
            "autostart": False,
            "check_updates": True
        }
        self.config = self.load_config()

    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return {**self.default_config, **json.load(f)}
            except Exception:
                pass
        return self.default_config.copy()

    def save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=4)

    def get(self, key, default=None):
        return self.config.get(key, default)

    def set(self, key, value):
        self.config[key] = value 
