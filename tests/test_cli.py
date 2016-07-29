import click
from click.testing import CliRunner
import cli
import os.path as path
from mock import Mock, MagicMock, patch
import mock

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
    @patch('jira.JIRA')
    @patch('csv.DictWriter')
    @patch('cli.get_config')

    def test_it_should_exit_if_no_config_is_present(self, mock_get_config, MockDictWriter, MockJira):
        runner = CliRunner()
        cli.get_config = lambda: ''

        result = runner.invoke(cli.download_all_data, ['foo.csv'])

        assert 'no config file detected' in result.output
        assert not cli.jira.JIRA.search_issues.called
        assert not cli.csv.DictWriter.called
        assert result.exit_code == 0
