import os
import sys

from setuptools import setup

setup(
    name='pgocli',
    version='0.1',
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
        'geopy',
        'tabulate'
    ],
    entry_points='''
    [console_scripts]
    pgo=pgocli.cli:cli
    ''',
)
