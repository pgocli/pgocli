import click


@click.group(short_help='Manage configuration')
@click.pass_context
def cli(ctx):  # pylint: disable=unused-argument
    pass


@cli.command(name='list',
             short_help='Display the saved configuration')
@click.pass_context
def cli_list(ctx):
    config = ctx.obj.get('config')

    click.secho('Displaying configuration from {}.\n'.format(
        config.get_path()
    ), bold=True)

    click.echo(config)


@cli.command(name='clear',
             short_help='Clear the saved configuration')
@click.confirmation_option(
    prompt='Are you sure you want to clear the configuration?'
)
@click.pass_context
def cli_clear(ctx):
    config = ctx.obj.get('config')

    config.clear()
    config.save()
