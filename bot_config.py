import configparser
import os


def set_config(file_path):
    config_parser = configparser.ConfigParser()
    config_parser.read(file_path)
    initial_config = {}
    for section in config_parser.sections():
        initial_config[section] = {}
        for key in config_parser[section]:
            initial_config[section][key] = config_parser[section][key]
    return initial_config


config_file_path = os.path.normpath('config.ini')
config = set_config(config_file_path)

json_file_path = config.get('auth', {}).get('json_file_path')
telegram_token = config.get('auth', {}).get('telegram_token')
admin_id = int(config.get('auth', {}).get('admin', 0))
language = config.get('auth', {}).get('language')
