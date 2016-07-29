#!/usr/bin/env python

import jira
import click
import json
import base64
import os.path as path
import csv
import warnings
import re
from collections import OrderedDict

warnings.filterwarnings('ignore')

OPTIONS = {
    'server': 'https://jira-ct.associatesys.local/',
    'verify': False
}

def get_config():
    return path.join(path.expanduser('~'), '.jira_getter.config.json')

def parse_config(config_file):
    #todo:  how should this behave when decoding fails?
    with open(config_file, 'r') as f:
        config = json.load(f)
    return (config['username'], base64.b64decode(config['password']))

def get_sprints(sprints):
    """scrapes a string for sprint name
    """
    sprint_name = re.compile('name=(.+?)\s*,')
    for sprint in sprints:
        print sprint_name.findall(sprint)
    return [sprint_name.findall(sprint) for sprint in sprints]

def process_issues(data):
    """fiddly processing logic for different field types
    """
    fields = data[0].raw['fields'].keys()
    fields.pop(fields.index('customfield_10406'))
    processed = []

    for issue in data:
        sprint_name_list = issue.fields.customfield_10406
        sprint_name = get_sprints(sprint_name_list) if sprint_name_list else None
        print sprint_name

        row = [
            ('name', issue.key),
            ('sprint', sprint_name),
        ]

        for field in fields:
            row.append((field, issue.raw['fields'].get(field)))

        processed.append(OrderedDict(row))

    return processed

@click.group()
def cli():
    """A global namespace for JIRA commands"""
    pass

@cli.command()
@click.option('--username', prompt=True)
@click.password_option()
def create_profile(username, password):
    """encodes and serializes JIRA login credentials

    passwords are encoded and stored on your home directory
    """
    #todo: check for existing file and ask for overwrite

    encoded_password = base64.b64encode(password)

    payload = {
        'username': username,
        'password': encoded_password
    }

    with open(get_config(), 'w') as f:
        json.dump(payload, f)
        click.secho("success!  config file written to: {}".format(get_config()), fg='green')

@cli.command()
@click.argument('output', type=click.File('wb'))
@click.argument('fields', nargs=-1)
def download_all_data(output, fields):
    """downloads all data from JIRA

    WARNING:  this operation will take several minutes
    """

    default_fields = ['customfield_10406', 'status', 'customfield_10143', 'resolutiondate']
    headers = default_fields + list(fields)
    fields = ','.join(headers)


    if not path.isfile(get_config()):
        click.secho("no config file detected.  please run cli.py create_profile first.", fg='red')
        return

    click.secho("Establishing connection to JIRA server...", fg='green')
    auth_tup = parse_config(get_config())
    jac = jira.JIRA(options=OPTIONS, basic_auth=auth_tup)

    click.secho("Fetching data...", fg='green')
    #todo: get this working async.  maybe check pathos?
    dev_issues = jac.search_issues('project = AMDG AND issuetype in (Defect, "Developer Story", Epic) AND sprint in ("DEV")',
                                    maxResults=10,
                                    fields=fields);

    writable = process_issues(dev_issues);
    click.secho("Writing file...", fg='green')
    writer = csv.DictWriter(output, fieldnames=writable[0].keys())
    writer.writeheader()
    writer.writerows(writable)

    click.secho("Success!", fg='green')


def get_data_for_sprint():
    pass

if __name__ == '__main__':
    cli()
