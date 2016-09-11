import base64
import csv
import datetime
import json
import os.path as path
import os
import warnings
from collections import OrderedDict
import sys
import keyring

import click
import jira

from jiranimo import decorators, utils
from jiranimo.issuecontainer import IssueContainer

warnings.filterwarnings('ignore')

# configs
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


@cli.group()
def get_data():
    """Get you some jira data"""
    pass

@profile.command()
@click.option('--username', prompt=True)
@click.password_option()
def create(username, password):
    """encodes and serializes JIRA login credentials

    passwords are stored on your system keychain
    """
    # todo: check for existing file and ask for overwrite

    keyring.set_password('system', username, password)
    click.secho('Credentials stored in keychain')
    payload = {
        'username': username,
    }

    with open(utils.get_config(), 'w') as f:
        json.dump(payload, f)
        click.secho("Success!  Config file written to: {}".format(
            utils.get_config()), fg='green')


@profile.command()
def delete():
    """delete login credentials"""
    prompt = click.style('This will remove login credentials from system keychain.  Do you want to continue?', fg='red')
    confirm = click.confirm(prompt, abort=True)
    if confirm:
        username = utils.parse_config(utils.get_config())[0]
        keyring.delete_password('system', username)
        os.remove(utils.get_config())
        click.secho("removed config file at {}".format(utils.get_config()), fg='green')



@get_data.command()
@click.argument('type', type=click.Choice(['dev', 'qa', 'hta']))
@click.argument('sprint_number', type=int)
@click.argument('output', type=click.Path(writable=False, dir_okay=False))
@click.option('--filetype', default='json', type=click.Choice(['csv', 'json']), help="Specify filetype")
@decorators.check_for_config_file
def sprint(type, sprint_number, output, filetype):
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
