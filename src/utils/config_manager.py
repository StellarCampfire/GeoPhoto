from configparser import ConfigParser
import os


class ConfigManager:
    def __init__(self, config_path='config.ini'):
        self.config_path = config_path
        self.config = ConfigParser()
        if not os.path.exists(self.config_path):
            self.create_default_config()
        self.load_config()

    def load_config(self):
        self.config.read(self.config_path)

    def create_default_config(self):
        self.config['logging'] = {
            'level': 'INFO',
            'path': 'logs/geo_photo_app.log',
            'format': '%(asctime)s - %(levelname)s - %(message)s'
        }
        self.config['logic'] = {
            'interval_step': '0.5',
            'interval_button_step': '0.05'
        }
        self.config['crop'] = {
            'left': '0',
            'right': '0',
            'top': '0',
            'bottom': '0'
        }
        self.config['camera'] = {
            'width': '0',
            'height': '0'
        }
        with open(self.config_path, 'w') as configfile:
            self.config.write(configfile)

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


if __name__ == "__main__":
    config_manager = ConfigManager()
    print(config_manager.get('logging', 'level'))
