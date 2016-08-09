# -*- coding: utf-8 -*-

import click
import time

from .inventory import Inventory


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

def require_steps(steps):
    for step in steps:
        if not step in INIT_STEPS:
            raise Exception('Unknown "{}" initialization step'.format(step))

    def require_steps_decorator(cmd):
        def cmd_wrapper(ctx, *args, **kwargs):
            api = ctx.obj.get('pgoapi')
            config = ctx.obj.get('config')

            if len(steps):
                with click.progressbar(length=len(steps) * 2, label='Initializing…') as bar:
                    for step in steps:
                        INIT_STEPS[step](ctx, api, config)
                        bar.update(1)
                        time.sleep(0.3)
                        bar.update(1)

                    click.echo()
            return cmd(ctx, *args, **kwargs)
        return cmd_wrapper
    return require_steps_decorator
