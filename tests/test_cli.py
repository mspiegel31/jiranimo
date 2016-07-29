import click
from click.testing import CliRunner
import cli
import os.path as path

HOME_DIRECTORY = path.expanduser('~')
CONFIG_FILE = path.join(HOME_DIRECTORY,'.jira_getter.config.json')

def test_get_sprints():
    test_data = ['name=abc, name=qqq,', 'asdlkasdasdoaiusdoaidaoisdausaoisudianame=ohyeah,', 'asdjaksddhasname=123,asdasdasdasdasdasdasdas']
    expected = [['abc', 'qqq'], ['ohyeah'], ['123']]
    result = cli.get_sprints(test_data)

    assert result == expected
