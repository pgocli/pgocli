# pgocli

## Development environment

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
$ docker run pgocli/pgocli pgo --help
```
