import click
import json
import os


class ConfigException(Exception):
    pass


class Config:
    def __init__(self, path):
        self._path = path

        if os.path.isfile(self._path):
            try:
                self.load()
            except ValueError:
                raise ConfigException(
                    'The specified configuration is not valid JSON'
                )

    def __unicode__(self):
        return json.dumps(
            self,
            default=lambda o: {
                k: getattr(o, k) for k in vars(o)
                if not str(k).startswith('_')
            },
            sort_keys=True,
            indent=4,
            ensure_ascii=False
        )

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __getattr__(self, name):
        if name not in self.__dict__:
            return None

        return self.__dict__[name]

    def get_path(self):
        return self._path

    def clear(self):
        for k in [k for k in self.__dict__ if not str(k).startswith('_')]:
            self.__dict__.pop(k, None)

    def load(self):
        with open(self._path, 'r') as f:
            self.__dict__.update(json.loads(f.read()))

    def save(self):
        with open(self._path, 'w+') as f:
            f.write(str(self))

            click.secho('\nThe configuration has been saved.', bold=True)
            click.echo(
                'Run `pgo config list` to display the saved configuration.'
            )
