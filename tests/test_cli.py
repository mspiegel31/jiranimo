import click
from click.testing import CliRunner
import cli
import os.path as path
import pytest
from mock import Mock, MagicMock, patch
import mock

class TestGetSprints:

    def test_it_should_extract_multiple_names(self):
        test_data = ['name=abc, name=qqq,']
        expected = [['abc', 'qqq']]
        result = cli.get_sprints(test_data)

        assert result == expected

    def test_it_should_extract_name_within_string(self):
        test_data = ['asdasdasdasdasdasdasdadname=qqq,asdasdasdasdasdasdads']
        expected = [['qqq']]
        result = cli.get_sprints(test_data)

        assert result == expected

    def test_it_should_strip_trailing_whitespaces(self):
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
        mock_get_config.return_value = ''
        result = runner.invoke(cli.download_all_data, ['foo.csv'])

        cli.jira.JIRA.search_issues.assert_not_called()
        cli.csv.DictWriter.assert_not_called()
        assert 'no config file detected' in result.output
        assert result.exit_code == 0

    @patch('cli.process_issues')
    @patch('csv.DictWriter')
    @patch('cli.parse_config')
    @patch('cli.path.isfile')
    @patch('cli.jira.JIRA')
    def test_it_should_request_a_default_set_of_fields(self, MockJira, mock_is_file, mock_parse_config, MockDictWriter, mock_process_issues):
        mock_is_file.return_value = True
        mock_parse_config.return_value = ('foo', 'bar')
        mock_jira_instance = MockJira.return_value
        default_fields = ','.join(['customfield_10406', 'status', 'customfield_10143', 'resolutiondate'])

        runner = CliRunner()
        result = runner.invoke(cli.download_all_data, ['foo.csv'])

        assert mock_jira_instance.search_issues.called
        mock_jira_instance.search_issues.assert_called_with('project = AMDG AND issuetype in (Defect, "Developer Story", Epic) AND sprint in ("DEV")', fields=default_fields, maxResults=10)

    @patch('cli.process_issues')
    @patch('csv.DictWriter')
    @patch('cli.parse_config')
    @patch('cli.path.isfile')
    @patch('cli.jira.JIRA')
    def test_it_should_request_a_default_set_of_fields(self, MockJira, mock_is_file, mock_parse_config, MockDictWriter, mock_process_issues):
        mock_is_file.return_value = True
        mock_parse_config.return_value = ('foo', 'bar')
        mock_jira_instance = MockJira.return_value
        default_fields = ['customfield_10406', 'status', 'customfield_10143', 'resolutiondate']
        additional_fields = ['1','2','3']

        expected_fields = ','.join(default_fields + additional_fields)

        runner = CliRunner()
        result = runner.invoke(cli.download_all_data, ['foo.csv'] + additional_fields)

        assert mock_jira_instance.search_issues.called
        mock_jira_instance.search_issues.assert_called_with('project = AMDG AND issuetype in (Defect, "Developer Story", Epic) AND sprint in ("DEV")', fields=expected_fields, maxResults=10)
