# -*- coding: utf-8 -*-

import click

from geopy.geocoders import GoogleV3
from geopy.exc import GeocoderQueryError

@click.command(name='position',
               short_help='Set the player\'s location')
@click.option('--position', required=True, prompt=True)
@click.pass_context
def cli(ctx, position):
    config = ctx.obj.get('config')

    # TODO: include google api key here
    geocoder = GoogleV3()

    try:
        loc = geocoder.geocode(position)

        if not loc:
            click.secho('Could not geocode the specified location, aborting…', fg='red')
            return False

        click.secho('Found position: {}'.format(loc.address.encode('utf8')), fg='cyan')
        config.position = dict(
            text=loc.address,
            latitude=loc.latitude,
            longitude=loc.longitude,
            altitude=loc.altitude
        )

        config.save()

    except GeocoderQueryError:
        click.secho('Could not geocode the specified location, aborting...', fg='red')
        return False
