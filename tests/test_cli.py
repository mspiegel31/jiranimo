import click
from click.testing import CliRunner
import cli
import os.path as path

HOME_DIRECTORY = path.expanduser('~')
CONFIG_FILE = path.join(HOME_DIRECTORY,'.jira_getter.config.json')

def test_create_profile():
    pass

def test_download_all_data():
    pass
