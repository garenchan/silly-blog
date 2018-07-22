#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os

import click


dir_name = os.path.abspath(os.path.dirname(__file__))
par_dir = os.path.join(dir_name, "..")
sys.path.append(par_dir)


@click.group()
def cli():
    pass


@cli.command()
@click.option("--host", default="127.0.0.1")
@click.option("--port", default=5000)
@click.option("--debug", is_flag=True, default=False, expose_value=True)
def runserver(host, port, debug):
    from silly_blog.app import app
    app.run(host, port, debug)


if __name__ == "__main__":
    cli()
