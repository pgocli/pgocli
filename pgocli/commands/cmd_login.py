# -*- coding: utf-8 -*-

import click

from ..context import require_steps


@click.command(name='login',
               short_help='Configure the authentication')
@click.argument('provider', required=True,
                type=click.Choice(['ptc', 'google']))
@click.option('--username', required=True, prompt=True)
@click.option('--password', required=True, prompt=True, hide_input=True)
@click.pass_context
@require_steps(['position'])
def cli(ctx, provider, username, password):
    api = ctx.obj.get('pgoapi')
    config = ctx.obj.get('config')

    if api.login(provider, username, password):
        click.secho('Login was successful!', fg='cyan')

        config.auth = dict(
            type=provider,
            username=username,
            password=password
        )

        config.save()

    else:
        click.secho('Login failed…', fg='red')
