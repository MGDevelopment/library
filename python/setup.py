#!/usr/bin/env python
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'ILHSA Ecommerce Module',
    'author':      'Jose Luis Campanello, Mariano Goldsman, Alejo Sanchez',
    'version':     '0.1',
    'packages':    ['ecommerce', 'ecommerce.config', 'ecommerce.db',
                    'ecommerce.content'],
    'requires':    ['pyaml', 'jinja2', 'psycopg'],
    'scripts':     [],
    'name':        'ecommerce'
}

setup(**config)
