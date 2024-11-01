import os

import setconfig

config_file_path = os.path.normpath('config.ini')
config = setconfig.set_config(config_file_path)
json_file_path = config.get('json_file_path')
telegram_token = config.get('telegram_token')
admin_id = int(config.get('admin'))
language = config.get('language')
