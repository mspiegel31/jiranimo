import jira
import click
import json
import base64
import os.path as path
import csv
import warnings

warnings.filterwarnings('ignore')

HOME_DIRECTORY = path.expanduser('~')
CONFIG_FILE = path.join(HOME_DIRECTORY,'.jira_getter.config.json')
OPTIONS = {
    'server': 'https://jira-ct.associatesys.local/',
    'verify': False
}





def get_config(config):
    with open(config, 'r') as f:
        data = json.load(f)

    return data

def parse_config(config):
    return (config['username'], base64.b64decode(config['password']))

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

    with open(CONFIG_FILE, 'w') as f:
        json.dump(payload, f)
        click.secho("success!  config file written to: {}".format(CONFIG_FILE), fg='green')




@cli.command()
def download_all_data():
    """downloads all data from JIRA

    WARNING:  this operation will take several minutes
    """

    if not path.isfile(CONFIG_FILE):
        click.secho("no config file detected.  please run cli.py create_profile first.", fg='red')
        return

    auth_tup = parse_config(get_config(CONFIG_FILE))
    jac = jira.JIRA(OPTIONS, basic_auth=auth_tup)



    click.echo("downloading")

if __name__ == '__main__':
    cli()
