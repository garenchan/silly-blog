#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os


dir_name = os.path.abspath(os.path.dirname(__file__))
par_dir = os.path.join(dir_name, "..")
sys.path.append(par_dir)


import click

from silly_blog.app import app, models


@app.shell_context_processor
def make_shell_context():
    """Use for drop shell
       1. set/export FLASK_APP=manage.py
       2. flask shell
    """
    from silly_blog.app import db
    return dict(
        app=app,
        db=db,
        models=models,
    )


@app.cli.command(with_appcontext=True)
def deploy():
    from silly_blog.app.models import Role, User, Category, Source
    Role.insert_default_values()
    User.insert_default_values()
    Category.insert_default_values()
    Source.insert_default_values()


@app.cli.command()
@click.option("--host", default="127.0.0.1")
@click.option("--port", default=5000)
@click.option("--debug", is_flag=True, default=False, expose_value=True)
def runserver(host, port, debug):
    app.run(host, port, debug)


if __name__ == "__main__":
    app.cli()
