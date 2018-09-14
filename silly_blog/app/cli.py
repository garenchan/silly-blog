# -*- coding: utf-8 -*-
import os

import click
from flask.cli import with_appcontext
from flask_migrate import cli


def migrate_cli_hack():
    """Hack `flask_migrate.cli`.

    By default, `flask_migrate.cli` commands use a directory named migrations
    under current work directory. We change the default value to a directory
    next to our app's root_path.
    """
    migrate = cli.migrate
    migrate.params[0].default = '123'
