# -*- coding: utf-8 -*-

import click
import os
import sys
import time

from pgoapi import PGoApi

from .config import Config
from .inventory import Inventory


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

    api.login(
        config.auth.get('type'),
        config.auth.get('username'),
        config.auth.get('password')
    )

def _init_player(ctx, api, config):
    if not config.auth:
        click.secho('\nAuthentication info was not set, run `pgo login` first.', fg='red')
        ctx.exit()

    request = api.create_request()
    request.get_player()
    request.get_hatched_eggs()
    request.get_inventory()
    request.check_awarded_badges()
    request.download_settings(hash="54b359c97e46900f87211ef6e6dd0b7f2a3ea1f5")
    responses = request.call().get('responses', {})

    ctx.obj['settings'] = responses   \
        .pop('DOWNLOAD_SETTINGS', {}) \
        .get('settings')

    ctx.obj['inventory'] = Inventory(
        responses
            .pop('GET_INVENTORY', {})    \
            .get('inventory_delta', {})  \
            .get('inventory_items')
    )

    ctx.obj['player'] = responses \
        .pop('GET_PLAYER', {})    \
        .get('player_data')

INIT_STEPS=dict(
    position=_init_position,
    login=_init_login,
    player=_init_player
)

@click.command(cls=MultiCommand)
@click.option('--config', '-c', type=click.Path(exists=True, resolve_path=True),
              help="JSON configuration file.")
@click.pass_context
def cli(ctx, config):
    config = Config(config or 'config.json')
    pgoapi = PGoApi()

    ctx.obj = dict(
        config=config,
        pgoapi=pgoapi
    )

    if ctx.invoked_subcommand in ['config', 'position']:
        steps=[]
    elif ctx.invoked_subcommand in ['login']:
        steps=['position']
    else:
        steps=['position', 'login', 'player']

    if len(steps):
        with click.progressbar(length=len(steps) * 2, label='Initializing…') as bar:
            for step in steps:
                if not step in INIT_STEPS:
                    raise Exception('Unknown "{}" initialization step'.format(step))

                INIT_STEPS[step](ctx, pgoapi, config)
                bar.update(1)
                time.sleep(0.3)
                bar.update(1)

            click.echo()
