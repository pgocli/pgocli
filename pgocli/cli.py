# -*- coding: utf-8 -*-

import click
import os
import sys

from pgoapi import PGoApi

from .config import Config


class Context:
    def __init__(self, **entries):
        self.__dict__.update(entries)

cmd_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), 'commands'))

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
            mod = __import__('pgocli.commands.cmd_' + name, None, None, ['cli'])
        except ImportError:
            return
        return mod.cli

def _init_position(ctx, api, config):
    if not config.position:
        click.secho('\nPosition was not set, run `pgo position` first.', fg='red')
        ctx.exit()

    api.set_position(
        config.position.get('latitude'),
        config.position.get('longitude'),
        config.position.get('altitude')
    )

def _init_login(ctx, api, config):
    if not config.auth:
        click.secho('\nAuthentication info was not set, run `pgo login` first.', fg='red')
        ctx.exit()

    return api.login(
        config.auth.get('type'),
        config.auth.get('username'),
        config.auth.get('password')
    )

INIT_STEPS=dict(
    position=_init_position,
    login=_init_login,
)

@click.command(cls=MultiCommand)
@click.option('--config', '-c', type=click.Path(exists=True, resolve_path=True),
              help="JSON configuration file.")
@click.pass_context
def cli(ctx, config):
    config = Config(config or 'config.json')
    pgoapi = PGoApi()

    if ctx.invoked_subcommand in ['config', 'position']:
        steps=[]
    elif ctx.invoked_subcommand in ['login']:
        steps=['position']
    else:
        steps=['position', 'login']

    if len(steps):
        with click.progressbar(length=len(steps), label='Initializing…') as bar:
            for step in steps:
                if not step in INIT_STEPS:
                    raise Exception('Unknown "{}" initialization step'.format(step))

                INIT_STEPS[step](ctx, pgoapi, config)
                bar.update(1)

            click.echo()

    ctx.obj = Context(
        config=config,
        pgoapi=pgoapi
    )
