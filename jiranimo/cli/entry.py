import click
from .subcommands import get_data, profile

@click.group()
def cli():
    """Utilities for getting data out of JIRA"""
    pass

cli.add_command(get_data)
cli.add_command(profile)

if __name__ == '__main__':
    cli()
