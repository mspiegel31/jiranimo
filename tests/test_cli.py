import click
from click.testing import CliRunner
import cli

def test_login():
    runner = CliRunner()
    result = runner.invoke(cli.login)
    assert result.exit_code == 0
    assert result.output == 'logging you in\n'
