import os.path as path
import unittest.mock as mock
from unittest.mock import MagicMock, Mock, patch

import click
import pytest
from click.testing import CliRunner

from jiranimo.cli.entry import cli
