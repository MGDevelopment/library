#!/usr/bin/env python
"""Config file loaders

This file contains a set of loaders that can be passed in to the
Config class. These loaders provide mechanisms for the configuration
to be read from different places
"""

from os.path import exists, join

defaultFolders = [ './config', '/etc/ecommerce' ]

defaultFragmentList = [ "global", "local", "keychain" ]

class ConfigLoader(object):
    """Base loader class"""

    def __init__(self, fragments = defaultFragmentList):
        self._fragments = fragments

    def loadFragment(self, fragment):
        """Loads the named config fragment"""

        raise NotImplementedError("loadFragment method not implemented")

    def hasFragment(self, fragment):
        """Figures out if a config fragment is available"""

        raise NotImplementedError("hasFragment method not implemented")

    def load(self):
        """Loads all the configuration fragments and returns a single string"""

        # load all fragments
        config = ""
        for f in self._fragments:
            fragment = self.loadFragment(f)
            if fragment is not None:
                config += self.loadFragment(f)
        return config


class ConfigLoaderFileSystem(ConfigLoader):
    """Load config from file system"""

    def __init__(self, folder, fragments = defaultFragmentList):
        ConfigLoader.__init__(self, fragments)
        self._folder = folder

    def loadFragment(self, fragment):
        """Load a config fragment from the specified folder (if exists)"""

        # check we have the file
        fileName = self._getFileName(fragment)
        if not exists(fileName):
            raise IOError('Fragment not found: ' + fragment)

        # open, read and close the file
        f = open(fileName, 'r')
        config = f.read()
        f.close()

        return config


    def hasFragment(self, fragment):
        """Figure out if the loader has access to the fragment"""

        return exists(self._getFileName(fragment))


    def _getFileName(self, fragment):
        """Returns the fragment file name"""

        return join(self._folder, fragment + ".yaml")


class ConfigLoaderMultiplexor(ConfigLoader):
    """Encapsulate multiple ConfigLoader objects"""

    def __init__(self, loaders, emptyFragments = False, fragments = defaultFragmentList):
        ConfigLoader.__init__(self, fragments)
        self._loaders = loaders
        self._emptyFragments = emptyFragments


    def loadFragment(self, fragment):
        """Try every loader until one returns the configuration fragment"""

        # try each loader
        for l in self._loaders:
            try:
                config = l.loadFragment(fragment)
            except:
                config = None
            if config is not None:
                return config

        # return empty or raise an exception
        if self._emptyFragments:
            return ""
        raise IOError('Fragment not found: ' + fragment)


    def hasFragment(self, fragment):
        """Try every loader until one says it has the fragment"""

        # try each loader
        for l in self._loaders:
            if l.hasFragment(fragment):
                return True
        return False


class ConfigLoaderStrings(ConfigLoader):
    """Load config from strings"""

    def __init__(self, configs, emptyFragments = False, fragments = defaultFragmentList):
        """Initialize the object

        The configs parameter must be a dictionary containing
        keys that match the fragments list.
        """
        ConfigLoader.__init__(self, fragments)
        self._configs = configs
        self._emptyFragments = emptyFragments


    def loadFragment(self, fragment):
        """Try every loader until one returns the configuration fragment"""

        # if we have the key, return that
        if self._configs.has_key(fragment):
            return self._configs.get(fragment)

        # return empty or raise an exception
        if self._emptyFragments:
            return ""
        raise IOError('Fragment not found: ' + fragment)


    def hasFragment(self, fragment):
        """Figure out if there is config for the requested fragment"""

        return self._configs.has_key(fragment) or self._emptyFragments

def getDefaultLoader():
    """Returns a default config file loader.

    The default loader consists of a multiplexor with a file loader for
    each default folder and returning empty defaults
    """

    # create the file system loaders
    loaders = [ ConfigLoaderFileSystem(f) for f in defaultFolders ]

    return ConfigLoaderMultiplexor(loaders, True)

