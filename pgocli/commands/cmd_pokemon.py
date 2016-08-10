import click
from tabulate import tabulate
import datetime
from collections import OrderedDict

from ..context import require_steps


def _format_iv(iv):
    iv_str = '{}%'.format(iv * 100)

    if iv == 1:
        iv_str = ' 100%'

    if iv < 0.1:
        iv_str = ' {}'.format(iv_str)

    if iv > 0.8:
        return click.style(iv_str, fg='green', bold=iv == 1)

    if iv > 0.6:
        return click.style(iv_str, fg='yellow')

    if iv < 0.2:
        return click.style(iv_str, fg='red')

    return iv_str


def _format_iv_value(value):
    if value == 15:
        return click.style(str(value), fg='green')

    if value > 13:
        return click.style(str(value), fg='yellow')

    if value < 5:
        return click.style(str(value), fg='red')

    return value


def _format_row(row):
    row['iv'] = _format_iv(row['iv'])
    row['iv_attack'] = _format_iv_value(row['iv_attack'])
    row['iv_defense'] = _format_iv_value(row['iv_defense'])
    row['iv_stamina'] = _format_iv_value(row['iv_stamina'])
    row['date'] = row['date'].isoformat(' ')
    return row


def _sort(key, rev=False):
    def sort_func(x, y):
        px = x.get(key)
        py = y.get(key)

        if rev:
            px, py = py, px

        if px is str:
            px = px.lower()
        if py is str:
            px = py.lower()

        return cmp(px, py)
    return sort_func


def _filter_date(date):
    today = datetime.date.today()

    if date == 'today':
        start = datetime.datetime(today.year, today.month, today.day)
        end = datetime.datetime.now()
    elif date == 'yesterday':
        start = datetime.datetime(today.year, today.month, today.day - 1)
        end = datetime.datetime(today.year, today.month, today.day)

    def filter_func(pokemon):
        return pokemon.caught_at > start and pokemon.caught_at < end

    return filter_func


@click.command(name='pokemon',
               short_help='List pokemon in the inventory')
@click.option(
    '--sort', '-s',
    type=click.Choice(['id', 'name', 'cp', 'iv', 'candy', 'nickname', 'date']),
    help='Sort pokemon list'
)
@click.option('--name', '-n', help='Filter by pokemon name')
@click.option(
    '--date', '-d',
    type=click.Choice(['today', 'yesterday']),
    help='Filter by catch date'
)
@click.option('--pager', '-p', is_flag=True, help='Display in a pager')
@click.pass_context
@require_steps(['position', 'login', 'player'])
def cli(ctx, sort, name, date, pager):
    inventory = ctx.obj.get('inventory')

    if not sort:
        sort = 'id'

    pokemon_list = inventory.pokemons.all()

    if name:
        pokemon_list = filter(
            lambda p: name.lower() in p.name.lower(),
            pokemon_list
        )

    if date:
        pokemon_list = filter(
            _filter_date(date),
            pokemon_list
        )

    data = [
        OrderedDict([
            ('id', p.pokemon_id),
            ('name', p.name),
            ('cp', p.cp),
            ('iv', p.iv),
            ('iv_attack', p.iv_attack),
            ('iv_defense', p.iv_defense),
            ('iv_stamina', p.iv_stamina),
            ('candy', inventory.candy.get(p.pokemon_id).quantity),
            ('nickname', p.nickname),
            ('date', p.caught_at)
        ])
        for p in pokemon_list
    ]

    if sort == 'id':
        data.sort(cmp=_sort('id'))
    elif sort == 'name':
        data.sort(cmp=_sort('name'))
    elif sort == 'cp':
        data.sort(cmp=_sort('cp', rev=True))
    elif sort == 'iv':
        data.sort(cmp=_sort('iv', rev=True))
    elif sort == 'candy':
        data.sort(cmp=_sort('candy', rev=True))
    elif sort == 'nickname':
        data.sort(cmp=_sort('nickname'))
    elif sort == 'date':
        data.sort(cmp=_sort('date', rev=True))

    table = tabulate(
        [
            _format_row(row)
            for row in data
        ],
        headers=OrderedDict(
            (head_id, click.style(head_title, bold=True))
            for head_id, head_title in [
                ('id', 'ID'),
                ('name', 'Name'),
                ('cp', 'CP'),
                ('iv', 'IV'),
                ('iv_attack', 'Attack'),
                ('iv_defense', 'Defense'),
                ('iv_stamina', 'Stamina'),
                ('candy', 'Candy'),
                ('nickname', 'Nickname'),
                ('date', 'Date')
            ]
        )
    )

    if pager:
        click.echo_via_pager(table)
    else:
        click.echo(table)
