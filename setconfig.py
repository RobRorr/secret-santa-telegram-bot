import configparser


def set_config(file_path):
    config = configparser.ConfigParser()
    config.read(file_path)
    initial_config = {}
    for section in config.sections():
        initial_config[section] = {}
        for key in config[section]:
            initial_config[section][key] = config[section][key]
    return initial_config['auth']
