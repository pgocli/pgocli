import click

from ..context import require_steps


def _echo_string(name, value):
    click.echo('{:27}: {}'.format(click.style(name, bold=True), value))


def _echo_int(name, value):
    _echo_string(name, '{:,}'.format(int(value)))


def _echo_float(name, value):
    _echo_string(name, '{:.2f}'.format(float(value)))


def _echo_fraction(name, num, den):
    _echo_string(name, '{:,} / {:,}'.format(int(num), int(den)))


@click.command(name='info',
               short_help='Display information about the player')
@click.pass_context
@require_steps(['position', 'login', 'player'])
def cli(ctx):
    config = ctx.obj.get('config')
    player = ctx.obj.get('player')
    inventory = ctx.obj.get('inventory')

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
    _echo_int('Coins', currency_coin)
    _echo_int('Stardust', currency_dust)
    click.echo()

    click.secho('[Player]', fg='magenta')
    _echo_int('Level', inventory.player.level)
    _echo_fraction(
        'XP',
        inventory.player.experience-inventory.player.prev_level_xp,
        inventory.player.next_level_xp-inventory.player.prev_level_xp
    )
    _echo_int('Total XP', inventory.player.experience)
    _echo_float('Km Walked', inventory.player.km_walked)
    _echo_int('Pokestops visits', inventory.player.poke_stop_visits)
    _echo_int('Encounters', inventory.player.pokemons_encountered)
    _echo_int('Captured', inventory.player.pokemons_captured)
    _echo_int('Throws', inventory.player.pokeballs_thrown)
    _echo_int('Eggs hatched', inventory.player.eggs_hatched)
    click.echo()

    pokedex_total = len(inventory.pokemons.STATIC_DATA)

    click.secho('[Pokedex]', fg='magenta')
    _echo_fraction('Seen', inventory.pokedex.total_seen(), pokedex_total)
    _echo_fraction(
        'Captured',
        inventory.pokedex.total_captured(), pokedex_total
    )
    click.echo()

    click.secho('[Pokemon]', fg='cyan')
    _echo_fraction(
        'Storage',
        inventory.pokemons.total_count(), player.get('max_pokemon_storage')
    )
    click.echo()

    click.secho('[Inventory]', fg='cyan')
    _echo_fraction(
        'Storage',
        inventory.items.total_count(), player.get('max_item_storage')
    )
    for item in inventory.items.all():
        _echo_int(item.name, item.count)
    click.echo()
