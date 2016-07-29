import click
from click.testing import CliRunner
import cli
import os.path as path
from mock import Mock, MagicMock, patch

HOME_DIRECTORY = path.expanduser('~')
CONFIG_FILE = path.join(HOME_DIRECTORY,'.jira_getter.config.json')


class TestGetSprints:

    def test_should_extract_multiple_names(self):
        test_data = ['name=abc, name=qqq,']
        expected = [['abc', 'qqq']]
        result = cli.get_sprints(test_data)

        assert result == expected

    def test_should_extract_name_within_string(self):
        test_data = ['asdasdasdasdasdasdasdadname=qqq,asdasdasdasdasdasdads']
        expected = [['qqq']]
        result = cli.get_sprints(test_data)

        assert result == expected

    def test_should_strip_trailing_whitespaces(self):
        test_data = ['name=requested name    ,']
        expected = [['requested name']]
        result = cli.get_sprints(test_data)
        assert result == expected

class TestDownloadAllData:
    # mock out config file
    # mock out jira connection
    # mock jira issue object
    # mock file writing;  assert that it happened
    def test_it_should_exit_if_no_config_is_present(self):
        runner = CliRunner()
        cli.config_file = ''
        result = runner.invoke(cli.download_all_data, ['mike.csv'])
        # assert jira context not called
        assert 'no config file detected' in result.output
        assert result.exit_code == 0
