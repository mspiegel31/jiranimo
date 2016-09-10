import os
import click
import sys
from lib import utils
from functools import wraps


def format_time(fn):
    @wraps(fn)
    def wrapper(*args, **kwarg):
        return fn(*args) / 60.0**2
    return wrapper


def check_for_config_file(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not os.path.isfile(utils.get_config()):
            click.secho(
                "No config file detected.  please run cli.py create_profile first.", fg='red')
            sys.exit(1)
        return fn(*args, **kwargs)
    return wrapper


def time(fn):
    """Times given function"""
    pass


def write(fn):
    """writes output of function """
    pass
