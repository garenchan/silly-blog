# -*- coding: utf-8 -*-
import os

import click
from flask.cli import with_appcontext
from flask_migrate import cli

BASE_DIR = os.path.dirname(__file__)
MIGRATIONS_DIR = os.path.abspath(
    os.path.join(BASE_DIR, os.path.pardir, 'migrations'))
TESTS_DIR = os.path.abspath(
    os.path.join(BASE_DIR, os.path.pardir, 'tests'))


@click.command('deploy')
@with_appcontext
def deploy_command():
    """Insert some default values into database while deployment."""
    from silly_blog.app.models import Role, User, Category, Source
    Role.insert_default_values()
    User.insert_default_values()
    Category.insert_default_values()
    Source.insert_default_values()
    click.echo('Initialized the database.')


@click.command('tests')
@with_appcontext
def tests_command():
    """Run unit tests."""
    import pytest
    pytest.main('--rootdir=%s' % TESTS_DIR)


def _db_upgrade_command():
    """Hack `flask_migrate.cli`.

    By default, `flask_migrate.cli` commands use a directory named migrations
    under current work directory. We change the default value to a directory
    next to our app's root_path.
    """
    upgrade = cli.upgrade
    param = upgrade.params[0]
    assert param.human_readable_name == 'directory'
    param.default = MIGRATIONS_DIR
    return upgrade


db_upgrade_command = _db_upgrade_command()
del _db_upgrade_command

# All commands which will be added
COMMANDS = (deploy_command, tests_command, db_upgrade_command)
