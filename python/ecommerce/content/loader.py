#!/usr/bin/env python
'''Template loader module for ILHSA SA
by Alejo Sanchez, Jose Luis Campanello and Mariano Goldsman
'''

from jinja2 import Environment, BaseLoader

class DBLoader(BaseLoader):
    '''Template loader from database
    
       params:
           conn: database connection object
           table: name of the table containing the templates
           column_name: name of the column of template names
           column_type: type of output of the template (html, js...)
           column_data: name of the column of template data
    '''
    def __init__(self, conn, table, column_name, column_data, column_type,
            line_statement_prefix = '#'):
        self._table = table
        self._column_name = column_name
        self._column_data = column_data
        self._column_type = column_type
        self._sql_list = 'SELECT %s FROM %s' % (column_name, table)
        self._sql_get  = 'SELECT * FROM %s WHERE %s IS ' %  \
                (column_data, table, column_name)
        # XXX

    def get_template(self, name):
        '''Get a template from the DB'''
        try:
            self._conn.execute(self._sql_get + name)
        except:
            # XXX
            pass

    def list_templates(self):
        try:
            tmpls = self.conn.execute(self.sql_list)
        except:
            # XXX


class RenderPage(object):
    '''Renders a specific page'''
