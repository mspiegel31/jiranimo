import json
import os

import click
import keyring
from jiranimo import utils


@click.group()
def profile():
    """Manage your login credentials"""
    pass


@profile.command()
@click.option('--username', prompt=True)
@click.password_option()
def create(username, password):
    """store username and password

    passwords are stored on your system keychain
    """
    # TODO: check for existing file and ask for overwrite

    keyring.set_password('system', username, password)
    click.secho('Credentials stored in keychain')
    payload = {
        'username': username,
    }

    with open(utils.get_config_path(), 'w') as f:
        json.dump(payload, f)
        click.secho("Success!  Config file written to: {}".format(
            utils.get_config_path()), fg='green')


@profile.command()
def delete():
    """delete login credentials"""
    prompt = click.style('This will remove login credentials from system keychain.  Do you want to continue?', fg='red')
    confirm = click.confirm(prompt, abort=True)
    if confirm:
        username = utils.parse_config(utils.get_config_path())[0]
        keyring.delete_password('system', username)
        os.remove(utils.get_config_path())
        click.secho("removed config file at {}".format(utils.get_config_path()), fg='green')
