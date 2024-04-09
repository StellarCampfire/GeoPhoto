from configparser import ConfigParser
import os


class ConfigManager:
    def __init__(self, config_path='config.ini'):
        self.config_path = config_path
        self.config = ConfigParser()
        self.load_config()

    def load_config(self):
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Config file{self.config_path} not founded.")
        self.config.read(self.config_path)

    def get(self, section, option, fallback=None):
        return self.config.get(section, option, fallback=fallback)

    def set(self, section, option, value):
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, option, value)
        self.save_config()

    def save_config(self):
        with open(self.config_path, 'w') as configfile:
            self.config.write(configfile)
