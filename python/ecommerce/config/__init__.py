#!/usr/bin/env python
'''Ecommerce module for ILHSA SA
by Alejo Sanchez, Jose Luis Campanello and Mariano Goldsman
'''

import re
from yaml       import safe_load

from loader     import *
from keychain   import *

class Config(object):
    '''Configuration parser

    Parameters:
    configLoader: the config loader to use
    '''
    def __init__(self, configLoader = None):
        # if no loader, get the default
        if configLoader is None:
            configLoader = loader.getDefaultLoader()

        # read and parse the configuration
        self.conf = safe_load(configLoader.load())

        # Prepare the regexp for get syntax
        self.__syntaxDot = re.compile("^\.?[\w\-\ ]+(\[\d+\])?(\.[\w\-\ ]+(\[\d+\])?)*$")

        # create a keychain object for this config
        self._keychain = Keychain(self)


    @property
    def keychain(self):
        """The keychain property"""
        return self._keychain


    def len(self):
        return len(self.conf)


    def fetchKey(self, key):
        return self.keychain.fetch(key)


    def __getitem__(self, key):
        """Support for config['path.key'] syntax"""
        return self.get(key)


    def getMulti(self, key1, key2, default=None):
        """Get from config with a splited key"""
        return self.get(key1 + "." + key2, default)


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


def getConfig(configLoader = None):
    """Return the configuration.

    The configuration is expected to be a singleton in the sense that
    parsing it multiple times to get the same result is sub-optimal.
    A SIGHUP signal shall be caugth to re-read the configuration.
    """
    global _cachedConfig

    # if needed, read the config
    if _cachedConfig is None:
        _cachedConfig = Config(configLoader)

    return _cachedConfig


def getConfigFromString(config = ""):
    """Return a Config object loaded with the passed in config."""

    # create a config object
    sLoaders = ConfigLoaderStrings( { "global" : config }, True)

    return Config(sLoaders)
