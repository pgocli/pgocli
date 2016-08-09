import os
import sys

from setuptools import setup

exec(open('pgocli/version.py').read())

setup(
    name='pgocli',
    version=__version__,
    description='',
    long_description='',
    classifiers=[],
    keywords='',
    author='',
    author_email='',
    url='',
    license='MIT',
    include_package_data=True,
    zip_safe=False,
    install_requires=[
    'click',
    'pgoapi',
    'tabulate'
    ],
    entry_points='''
    [console_scripts]
    pgo=pgocli.cli:cli
    ''',
)
