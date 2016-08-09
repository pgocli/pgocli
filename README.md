# pgocli [![CircleCI](https://circleci.com/gh/pgocli/pgocli.svg?style=svg)](https://circleci.com/gh/pgocli/pgocli)

[![Code Health](https://landscape.io/github/pgocli/pgocli/master/landscape.svg?style=flat)](https://landscape.io/github/pgocli/pgocli/master)

## Development

```shell
$ virtualenv env
$ source env/bin/activate
$ pip install -r requirements.txt
$ pip install -e .

$ pgo --help
```

## Docker

```shell
$ docker pull pgocli/pgocli
$ docker run -it pgocli/pgocli bash
$ cd /opt/pgocli

$ pgo --help
$ pgo position
$ pgo login AUTH_SERVICE
$ pgo pokemon
```

## Test

```shell
$ pip install tox
$ tox
```
