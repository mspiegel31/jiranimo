#!/usr/bin/env python

import jira
import click
import json
import base64
import os.path as path
import csv
import warnings
import re
import requests
from collections import OrderedDict
from lib.issuecontainer import IssueContainer

warnings.filterwarnings('ignore')
AMDG_BOARD_ID = 2164

OPTIONS = {
    'server': 'https://jira-ct.associatesys.local',
    'verify': False
}

issue_path = '/rest/agile/1.0/board/{boardId}/sprint/{sprintId}/issue'
issue_url = OPTIONS['server'] + issue_path


def get_config():
    return path.join(path.expanduser('~'), '.jira_getter.config.json')


def parse_config(config_file):
    # todo:  how should this behave when decoding fails?
    with open(config_file, 'r') as f:
        config = json.load(f)
    return (config['username'], base64.b64decode(config['password']))


def get_sprints(sprints):
    """scrapes a string for sprint name
    """
    sprint_name = re.compile('name=(.+?)\s*,')
    return [sprint_name.search(sprint).group(1) for sprint in sprints]


def process_issues(data):
    """fiddly processing logic for different field types
    """
    fields = data[0].raw['fields'].keys()
    fields.pop(fields.index('customfield_10406'))
    processed = []

    for issue in data:
        sprint_name_list = issue.fields.customfield_10406
        sprint_name = get_sprints(
            sprint_name_list) if sprint_name_list else None

        row = [
            ('name', issue.key),
            ('sprint', sprint_name),
        ]

        for field in fields:
            if field == 'status':
                row.append((field, issue.raw['fields'].get(field)['name']))
            elif 'time' in field:
                row.append((field, issue.raw['fields'].get(
                    field) / 60.0**2 if issue.raw['fields'].get(field) else 0))
            else:
                row.append((field, issue.raw['fields'].get(field)))

        processed.append(OrderedDict(row))

    return processed


def create_filename(name, filetype):
    name = name.replace('.' + filetype, '')
    return '.'.join([name, filetype])


@click.group()
def cli():
    """Utilities for getting data out of JIRA"""
    pass


@cli.command()
@click.option('--username', prompt=True)
@click.password_option()
def create_profile(username, password):
    """encodes and serializes JIRA login credentials

    passwords are encoded and stored on your home directory
    """
    # todo: check for existing file and ask for overwrite

    encoded_password = base64.b64encode(password)

    payload = {
        'username': username,
        'password': encoded_password
    }

    with open(get_config(), 'w') as f:
        json.dump(payload, f)
        click.secho("Success!  Config file written to: {}".format(
            get_config()), fg='green')


@cli.command()
@click.argument('type', type=click.Choice(['dev', 'qa', 'hta']))
@click.argument('sprint_number', type=int)
@click.argument('output', type=click.Path(writable=False, dir_okay=False))
@click.option('--filetype', default='json', type=click.Choice(['csv', 'json']), help="Specify filetype")
def get_data_for_sprint(type, sprint_number, output, filetype):
    """Get a snapshot of the issue status for the given sprint"""
    # todo: make this a decorator
    if not path.isfile(get_config()):
        click.secho(
            "No config file detected.  please run cli.py create_profile first.", fg='red')
        return

    auth_tup = parse_config(get_config())
    click.secho("Establishing connection to JIRA server...", fg='green')
    gh = jira.client.GreenHopper(OPTIONS)

    click.secho("Fetching data...", fg='green')
    sprints = gh.sprints(AMDG_BOARD_ID)
    requested_sprint_id = [sprint for sprint in sprints if str(
        sprint_number) in sprint.name and type.upper() in sprint.name].pop().id
    sprint_url = issue_url.format(
        boardId=AMDG_BOARD_ID, sprintId=requested_sprint_id)

    # todo:  logging/error for when request fails
    print sprint_url
    response = requests.get(sprint_url, auth=auth_tup, verify=False)
    if not response.ok:
        click.secho('connection refused with status_code {}: {} '.format(
            response.status_code, response.reason), fg='red')
        return

    click.secho('Processing...', fg='green')
    sprint_data = response.json()

    data = []
    for issue in sprint_data['issues']:
        issue_data = IssueContainer(issue)._asdict()
        issue_data.pop('raw')
        issue_data['sprint'] = sprint_number
        issue_data['type'] = type
        data.append(issue_data)

    click.secho("Writing file...", fg='green')
    filename = create_filename(output, filetype)
    with open(filename, 'wb') as f:
        json.dump(data, f, indent=2)

    click.secho("Success!", fg='green')


@cli.command()
@click.argument('output', type=click.Path(writable=False, dir_okay=False))
@click.argument('fields', nargs=-1)
@click.option('--filetype', default='csv', type=click.Choice(['csv', 'json']), help="Specify filetype")
def download_all_data(output, fields, filetype):
    """downloads all data from JIRA

    WARNING:  this operation will take several minutes
    """

    default_fields = ['customfield_10406', 'status',
                      'customfield_10143', 'resolutiondate',
                      'aggregatetimespent', 'aggregatetimeoriginalestimate']
    headers = default_fields + list(fields)
    fields = ','.join(headers)

    if not path.isfile(get_config()):
        click.secho(
            "no config file detected.  please run cli.py create_profile first.", fg='red')
        return

    click.secho("Establishing connection to JIRA server...", fg='green')
    auth_tup = parse_config(get_config())
    jac = jira.JIRA(options=OPTIONS, basic_auth=auth_tup)

    click.secho("Fetching data...", fg='green')

    # todo: get this working async.  maybe check pathos?
    dev_issues = jac.search_issues('project = AMDG AND issuetype in (Defect, "Developer Story", Epic) AND sprint in ("DEV")',
                                   maxResults=10,
                                   fields=fields)

    writable = process_issues(dev_issues)

    click.secho("Writing file...", fg='green')

    filename = create_filename(output, filetype)
    if filetype == 'csv':
        with open(filename, 'wb') as f:
            writer = csv.DictWriter(f, fieldnames=writable[0].keys())
            writer.writeheader()
            writer.writerows(writable)

    elif filetype == 'json':
        with open(filename, 'wb') as f:
            json.dump(writable, f, indent=2)

    click.secho("Success!", fg='green')


if __name__ == '__main__':
    cli()
