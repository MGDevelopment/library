#!/usr/bin/env python
'''Render module for ILHSA SA
by Alejo Sanchez, Jose Luis Campanello and Mariano Goldsman
'''

from jinja2 import Environment, FunctionLoader

env = Environment(loader=PackageLoader('tmk', 'templates'),
        line_statement_prefix='#')

# TODO: This must be read from a configuration file
render_context = { 'lang'  : 'es', 'output' : 'out' }

#
# Render index page
#
template = env.get_template('index.html')

print template.render(render_context, title='Tematika')

class RenderPage(object):
    '''Renders a specific page'''
