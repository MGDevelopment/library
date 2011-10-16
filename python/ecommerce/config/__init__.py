#!/usr/bin/env python
'''Ecommerce module for ILHSA SA
by Alejo Sanchez, Jose Luis Campanello and Mariano Goldsman
'''
from os.path import exists, join
from sys import exc_info
import re
from yaml import safe_load

global_name = 'global.yaml'
local_name  = 'local.yaml'

dirs = [ './config', '/etc/ecommerce' ] # Directories to find XXX S3

def find_file(name, paths):
    '''Find an existing file in a list of paths'''
    for dir in paths:
        fn = join(dir, name)
        if exists(fn):
            return fn
    raise IOError('File not found: ' + name)

def merge_files(*args):
    '''Open multiple files and return content concatenated'''
    if len(args) == 0:
        return ''
    ret = ''
    for f in args:
        fd = open(f, 'r')
        ret += fd.read() # join strings
        # FIX - jcampanello - could cause ENFILE if args is long
        fd.close()
    return ret

class Config(object):
    '''Configuration parser

    Parameters:
    paths:   paths where to look up configuration files
    fglobal: file name for global configuration file
    flocal:  file name for local configuration file
    '''
    def __init__(self, paths=dirs, fglobal=global_name, flocal=local_name):
        # Open and concatenate files
        # Find global file
        self.conf = safe_load(merge_files(find_file(fglobal, paths),
                                          find_file(flocal,  paths)))

        # Prepare the regexp for get syntax
        self.__syntaxDot = re.compile("^\.?[\w\-\ ]+(\[\d+\])?(\.[\w\-\ ]+(\[\d+\])?)*$")


    def len(self):
        return len(self.conf)


    def __getitem__(self, key):
        """Support for config['path.key'] syntax"""
        return self.get(key)


    def getMulti(self, key1, key2, default=None):
        """Get from config with a splited key"""
        return self.get(key1 + key2, default)


    def get(self, key, default=None):
        """Get from config using an simplified doted syntax

        Doing get("some.array[0].node") is equivalent to
        doing "conf['some']['array'][0]['node']".

        Parameters:
        key --- the key to find
        default --- the default value to return if key is not present
        """

        # check expression syntax
        path = None
        if self.__syntaxDot.match(key) is not None:
            path = key.split(".")
        if path is None:
            # not a doted key
            raise KeyError('invalid syntax for key [%s]' % key)

        # remove first and last empty items (if present)
        if path[0] == '' :
            path = path[1:]
        if path[-1] == '' :
            path = path[:-1]

        try:
            tree = self.conf
            
            for x in path:

                # still have path but tree is empty => exception
                if tree is None:
                    raise KeyError('key [%s] not found' % key)

                # if it's of the form key[elem] handle differently
                pos = x.find('[')
                if pos != -1:
                   index = int(x[pos + 1:-1])
                   tree = tree[x[:pos]][index]
                else:
                   tree = tree[x]
            return tree
        except:
            return default


_cachedConfig = None


def getConfig(paths=dirs, fglobal=global_name, flocal=local_name):
    """Return the configuration.

    The configuration is expected to be a singleton in the sense that
    parsing it multiple times to get the same result is sub-optimal.
    A SIGHUP signal shall be caugth to re-read the configuration.
    """
    global _cachedConfig

    # if needed, read the config
    if _cachedConfig is None:
        _cachedConfig = Config(paths, fglobal, flocal)

    return _cachedConfig

