#!/usr/bin/env python
"""Config file keychain

This file contains a class that implements password management. The
class is created inside a Config object and handles access to
passwords.
"""

from os.path   import exists, join as os_path_join
from yaml      import safe_load

from loader    import *

defaultConfig = """
---
keychain:
  file:     keychain.yaml
  dirs:
    - ./config
    - /etc/ecommerce
"""

class Keychain(object):
    """Keychain class

    The Keychain is contained in a separate file. Each key (password)
    has a name. In this implementation passwords are stored in cleartext,
    but the existence of the class provides for a mechanism to have them
    encrypted.

    Keys are accessed by name. The method "fetch" receives a key name and
    returns the decrypted password. Key names are represented by a string
    of the form "keychain:{keyname}". If the method "fetch" receives an
    input that does not conform to that syntax, it returns the same value.
    This allows for keys to be stored cleartext in config files without
    requiring the application to be aware of which keys are encrypted.
    The application can just get the password attribute and pass the value
    thru the keychain, which will decrypt if encrypted or do nothing.

    Two configuration variables are required:
    - keychain.file (default keychain.yaml)
    - keychain.dirs (defaults to [ "./config", "/etc/ecommerce" ])
    """

    def __init__(self, config = None):

        # be sure we have a config or create one with default values
        if config is None:
            config = getConfigFromString(defaultConfig)

        # get the config
        self._fileName = config.get("keychain.file")
        self._dirNames = config.get("keychain.dirs", [ ])

        # find and load the keychain file
        self._fullPath = self._keychainFind()
        self._keychain = self._keychainLoad()


    def _keychainFind(self):
        """Finds the keychain file"""

        # iterate each dir
        for d in self._dirNames:

            # build the expected name
            fullPath = os_path_join(d, self._fileName)

            # if exists, return that
            if exists(fullPath):
                return fullPath

        # fail
        #####raise IOError('Keychain file [%s] not found' % self._fileName)
        return None


    def _keychainLoad(self):
        """Loads the keychain file"""

        # only if it makes sense
        if self._fullPath is None:
            return { }      # empty keychain

        # read the file content
        f = open(self._fullPath, "r")
        keys = f.read()
        f.close()

        # parse the keychain
        return safe_load(keys)


    def fetch(self, key):
        """Fetches the given key from the keychain

        If key does not conform to the syntax "keychain:{keyname}"
        it is returned without any change. If the key named "{keyname}"
        is not found, an KeyError exception is raised
        """

        # if doesn't match the keychain syntax, return as is
        if not key.startswith("keychain:"):
            return key

        # get the key name
        keyName = key[len("keychain:"):]

        # if the key is not in the keychain, raise
        if keyName not in self._keychain:
            raise KeyError("Key [%s] not in keychain" % keyName)

        # TODO - complete this with algorithms to fetch the real password

        # for now, return the value as is
        return self._keychain[keyName]["value"]

