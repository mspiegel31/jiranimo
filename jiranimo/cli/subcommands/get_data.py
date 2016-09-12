import csv
import datetime
import json
import sys
import warnings
from collections import OrderedDict

import click
from jiranimo import decorators, utils
from jiranimo.issuecontainer import IssueContainer

# configs
warnings.filterwarnings('ignore')
AMDG_BOARD_ID = 2164
OPTIONS = {
    'server': 'https://jira-ct.associatesys.local',
    'verify': False
}

fields = ','.join(IssueContainer.field_mappings.values())


@click.group()
def get_data():
    """Get you some jira data"""
    pass


@get_data.command()
@click.argument('type', type=click.Choice(['dev', 'qa', 'hta']))
@click.argument('sprint_number', type=int)
@click.argument('output', type=click.Path(writable=False, dir_okay=False))
@click.option('--filetype', default='json', type=click.Choice(['csv', 'json']), help="Specify filetype")
@decorators.check_for_config_file
def sprint(type, sprint_number, output, filetype):
    """Get a snapshot of the issue status for the given sprint"""

    # TODO make this a function/decorator
    click.secho("Establishing connection to JIRA server...", fg='green')
    auth_tup = utils.parse_config(utils.get_config_path())
    gh = jira.client.GreenHopper(OPTIONS)
    jac = jira.JIRA(options=OPTIONS, basic_auth=auth_tup)

    sprints = gh.sprints(AMDG_BOARD_ID)
    requested_sprint = utils.filter_sprints(sprints, sprint_number, type)

    if not requested_sprint:
        click.secho('Could not find sprint "{} - {}". Are you sure there is data for this sprint?'.format(sprint_number, type.upper()), fg='red')
        sys.exit(1)

    click.secho("Fetching data for {}".format(requested_sprint.name), fg='green')

    # TODO:  logging/error for when request fails
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

    # TODO make this a function/decorator
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
