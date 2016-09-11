import json
import os
import keyring

def create_filename(name, filetype):
    name = name.replace('.' + filetype, '')
    return '.'.join([name, filetype])


def get_config_path():
    return os.path.join(os.path.expanduser('~'), '.jira_getter.config.json')

def filter_sprints(sprint_list, num, type):
    template = 'Sprint {id} - {type}'
    sprint_query = template.format(id=num, type=type)
    requested_sprint = [sprint for sprint in sprint_list if sprint_query.lower() in sprint.name.lower()]
    return requested_sprint.pop() if requested_sprint else None

def parse_config(config_file):
    # todo:  how should this behave when decoding fails?
    with open(config_file, 'r') as f:
        config = json.load(f)

    password = keyring.get_password('system', config['username'])
    return (config['username'], password)
