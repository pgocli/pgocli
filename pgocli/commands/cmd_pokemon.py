import click
from tabulate import tabulate

from ..context import require_steps


def _format_iv(iv):
    return int(iv * 100)


@click.command(name='pokemon',
               short_help='List pokemon in the inventory')
@click.option(
    '--sort', '-s',
    type=click.Choice(['id', 'name', 'cp', 'iv', 'candy', 'nickname'])
)
@click.option('--pager', '-p', is_flag=True)
@click.pass_context
@require_steps(['position', 'login', 'player'])
def cli(ctx, sort, pager):
    inventory = ctx.obj.get('inventory')

    if not sort:
        sort = 'id'

    data = [
        [
            p.pokemon_id,
            p.name,
            p.cp,
            _format_iv(p.iv),
            p.iv_attack,
            p.iv_defense,
            p.iv_stamina,
            inventory.candy.get(p.pokemon_id).quantity,
            p.nickname
        ]
        for p in inventory.pokemons.all()
    ]

    if sort == 'id':
        data.sort(cmp=lambda x, y: cmp(x[0], y[0]))
    elif sort == 'name':
        data.sort(cmp=lambda x, y: cmp(x[1].lower(), y[1].lower()))
    elif sort == 'cp':
        data.sort(cmp=lambda x, y: cmp(y[2], x[2]))
    elif sort == 'iv':
        data.sort(cmp=lambda x, y: cmp(y[3], x[3]))
    elif sort == 'candy':
        data.sort(cmp=lambda x, y: cmp(y[7], x[7]))
    elif sort == 'nickname':
        data.sort(cmp=lambda x, y: cmp(x[8].lower(), y[8].lower()))

    table = tabulate(data, headers=[
        click.style(head, bold=True)
        for head in [
            'ID',
            'Name',
            'CP',
            'IV',
            'Attack',
            'Defense',
            'Stamina',
            'Candy',
            'Nickname'
        ]
    ])

    if pager:
        click.echo_via_pager(table)
    else:
        click.echo(table)
