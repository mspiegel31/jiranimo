#!/usr/bin/env python3

import base64
import csv
import datetime
import json
import os.path as path
import re
import warnings
from collections import OrderedDict
import sys

import click
import jira
import requests

from lib import decorators, utils
from lib.issuecontainer import IssueContainer

warnings.filterwarnings('ignore')
AMDG_BOARD_ID = 2164

OPTIONS = {
    'server': 'https://jira-ct.associatesys.local',
    'verify': False
}

fields = ','.join(IssueContainer.field_mappings.values())


@click.group()
def cli():
    """Utilities for getting data out of JIRA"""
    pass


@cli.group()
def profile():
    """options for managing login credentials"""
    pass


@profile.command()
@click.option('--username', prompt=True)
@click.password_option()
def create(username, password):
    """encodes and serializes JIRA login credentials

    passwords are encoded and stored on your home directory
    """
    # todo: check for existing file and ask for overwrite

    encoded_password = base64.b64encode(password.encode()).decode()

    payload = {
        'username': username,
        'password': encoded_password
    }

    with open(utils.get_config(), 'w') as f:
        json.dump(payload, f)
        click.secho("Success!  Config file written to: {}".format(
            utils.get_config()), fg='green')


@profile.command()
def delete():
    """delete login credentials"""
    click.secho('not yet implemented', fg='red')


@cli.command()
@click.argument('type', type=click.Choice(['dev', 'qa', 'hta']))
@click.argument('sprint_number', type=int)
@click.argument('output', type=click.Path(writable=False, dir_okay=False))
@click.option('--filetype', default='json', type=click.Choice(['csv', 'json']), help="Specify filetype")
@decorators.check_for_config_file
def get_data_for_sprint(type, sprint_number, output, filetype):
    """Get a snapshot of the issue status for the given sprint"""

    #todo make this a function/decorator
    click.secho("Establishing connection to JIRA server...", fg='green')
    auth_tup = utils.parse_config(utils.get_config())
    gh = jira.client.GreenHopper(OPTIONS)
    jac = jira.JIRA(options=OPTIONS, basic_auth=auth_tup)

    sprints = gh.sprints(AMDG_BOARD_ID)
    requested_sprint = utils.filter_sprints(sprints, sprint_number, type)

    if not requested_sprint:
        click.secho('Could not find sprint "{} - {}". Are you sure there is data for this sprint?'.format(sprint_number, type.upper()), fg='red')
        sys.exit(1)

    click.secho("Fetching data for {}".format(requested_sprint.name), fg='green')

    # todo:  logging/error for when request fails
    sprint_data = jac.search_issues('project = AMDG and sprint = {sprintId}'.format(sprintId=requested_sprint.id),
                                    maxResults=100,
                                    fields=fields)

    click.secho('Processing...', fg='green')
    today = datetime.datetime.utcnow().date()
    common = [
        ('date_downloaded', str(today)),
        ('sprint', sprint_number),
        ('type', type)
    ]
    data = []
    for issue in sprint_data:
        issue_data = IssueContainer(issue.raw)._asdict()
        issue_data.pop('raw')
        data.append(OrderedDict(common + list(issue_data.items())))

    #todo make this a function/decorator
    click.secho("Writing file...", fg='green')
    filename = utils.create_filename(output, filetype)
    if filetype == 'csv':
        with open(filename, 'w') as f:
            writer = csv.DictWriter(f, fieldnames=list(data[0].keys()))
            writer.writeheader()
            writer.writerows(data)

    elif filetype == 'json':
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)

    click.secho("Success!", fg='green')

if __name__ == '__main__':
    cli()
