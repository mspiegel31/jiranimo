import jira
import click
import json

@click.command()
def login():
    click.echo("logging you in")


if __name__ == '__main__':
    login()
