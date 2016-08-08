import click

@click.command(name='login',
               short_help='Configure the authentication')
@click.argument('type', required=True, type=click.Choice(['ptc', 'google']))
@click.option('--username', required=True, prompt=True)
@click.option('--password', required=True, prompt=True, hide_input=True)
@click.pass_context
def cli(ctx, type, username, password):
    if ctx.obj.pgoapi.login(type, username, password):
        click.secho('Login was successful!', fg='cyan')

        ctx.obj.config.auth = dict(
            type=type,
            username=username,
            password=password
        )

        ctx.obj.config.save()
