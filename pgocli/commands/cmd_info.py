import click
import json

def _echo_string(name, value):
    click.echo('{:22}: {}'.format(click.style(name, bold=True), value))

def _echo_number(name, value):
    _echo_string(name, '{:,}'.format(int(value)))

@click.command(name='info',
               short_help='Display information about the player')
@click.pass_context
def cli(ctx):
    config = ctx.obj.get('config')
    player = ctx.obj.get('player')

    click.secho('[General]', fg='')
    _echo_string('Username', player.get('username'))
    if 'text' in config.position:
        _echo_string('Address', config.position.get('text').encode('utf8'))
    _echo_string('Latitude', config.position.get('latitude'))
    _echo_string('Longitude', config.position.get('longitude'))
    _echo_string('Map', 'https://www.google.com/maps/@{},{},17z'.format(
        config.position.get('latitude'),
        config.position.get('longitude'),
    ))
    click.echo()

    currency_coin = player['currencies'][0].get('amount', 0)
    currency_dust = player['currencies'][1].get('amount', 0)

    click.secho('[Currencies]', fg='yellow')
    _echo_number('Coins', currency_coin)
    _echo_number('Stardust', currency_dust)
    click.echo()

    click.secho('[Inventory]', fg='cyan')
    _echo_number('Storage size', player.get('max_item_storage'))
    click.echo()

    click.secho('[Pokemon]', fg='cyan')
    _echo_number('Storage size', player.get('max_pokemon_storage'))
    click.echo()
