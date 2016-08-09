# -*- coding: utf-8 -*-

import click
import os
import sys

from importlib import import_module
from pgoapi import PGoApi

from .config import Config


cmd_folder = os.path.abspath(
    os.path.join(os.path.dirname(__file__), 'commands')
)


class MultiCommand(click.MultiCommand):
    def list_commands(self, ctx):
        rv = []
        for filename in os.listdir(cmd_folder):
            if filename.endswith('.py') and \
               filename.startswith('cmd_'):
                rv.append(filename[4:-3])
        rv.sort()
        return rv

    def get_command(self, ctx, name):
        try:
            if sys.version_info[0] == 2:
                name = name.encode('ascii', 'replace')
            mod = import_module('.commands.cmd_' + name, package='pgocli')
        except ImportError:
            return
        return mod.cli


@click.command(cls=MultiCommand)
@click.option('--config', '-c', help='JSON configuration file.',
              type=click.Path(exists=True, resolve_path=True))
@click.pass_context
def cli(ctx, config):
    config = Config(config or 'config.json')
    pgoapi = PGoApi()

    ctx.obj = dict(
        config=config,
        pgoapi=pgoapi
    )
