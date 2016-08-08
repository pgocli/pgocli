import click

from geopy.geocoders import GoogleV3

@click.command(name='info',
               short_help='Display information about the player')
@click.pass_context
def cli(ctx):
    pass
