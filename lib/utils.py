import os
import json
import base64


def create_filename(name, filetype):
    name = name.replace('.' + filetype, '')
    return '.'.join([name, filetype])

def get_config():
    return os.path.join(os.path.expanduser('~'), '.jira_getter.config.json')

def parse_config(config_file):
    # todo:  how should this behave when decoding fails?
    with open(config_file, 'r') as f:
        config = json.load(f)
    return (config['username'], base64.b64decode(config['password']))
