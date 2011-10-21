#!/usr/bin/env python
from distutils.core import setup
from commands import TestCommand, CleanCommand

config = {
    'description': 'ILHSA Ecommerce Module',
    'author':      'Jose Luis Campanello, Mariano Goldsman, Alejo Sanchez',
    'version':     '0.1',
    'packages':    ['ecommerce',
                    'ecommerce.config',
                    'ecommerce.db',
                    'ecommerce.content'],
    'requires':    ['yaml', 'jinja2', 'psycopg', 'boto'],
    'scripts':     [],
    'name':        'ecommerce',
    'cmdclass' : {
        'test': TestCommand,
        'clean': CleanCommand
    }
}

setup(**config)
