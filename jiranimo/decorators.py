import os
import sys
from functools import wraps

import click

from jiranimo import utils


def check_for_config_file(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not os.path.isfile(utils.get_config()):
            click.secho(
                "No config file detected.  please run cli.py create_profile first.", fg='red')
            sys.exit(1)
        return fn(*args, **kwargs)
    return wrapper


def write(fn):
    """writes output of function """
    pass

def time(fn):
    """Times given function"""
    pass
